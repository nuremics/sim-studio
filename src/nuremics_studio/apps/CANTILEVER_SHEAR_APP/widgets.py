import os
import json
import re
import shutil
from pathlib import Path

import marimo as mo
import pyvista as pv
import pandas as pd
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepTools import breptools
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import topods
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Display.WebGl import x3dom_renderer


def settings(
    working_path: Path,
    list_paths: list,
    set_state: mo.state,
) -> tuple[dict, dict]:
    
    widget_paths = {}
    dict_widget_paths = {}
    for path in list_paths:

        if path == "mesh_settings.json":

            file_path = working_path / path
            if file_path.exists():
                with open(file_path) as f:
                    dict_inputs = json.load(f)
            else:
                dict_inputs = {
                    "elem": "hexa",
                    "nb_elem_length": 100,
                    "nb_elem_width": 1,
                    "nb_elem_height": 1,
                }
                with open(file_path, "w") as f:
                    json.dump(dict_inputs, f, indent=4)
            
            list_widget = []
            dict_widget_paths[path] = {}
            for key, value in dict_inputs.items():

                if type(value) == str:
                    w = mo.ui.dropdown(
                        options=["hexa", "tetra"],
                        label=f"{key}:",
                        value=value,
                    )
                else:
                    w = mo.ui.number(
                        label=f"{key}:",
                        step=1,
                        value=value,
                        on_change=set_state,
                    )
                list_widget.append(w)
                dict_widget_paths[path][key] = w
            
            widget = mo.vstack(list_widget)
            widget_paths[path] = widget

        if path == "time_settings.json":

            file_path = working_path / path
            if file_path.exists():
                with open(file_path) as f:
                    dict_inputs = json.load(f)
            else:
                dict_inputs = {
                    "ramp": 100.0,
                    "final_time": 200.0,
                }
                with open(file_path, "w") as f:
                    json.dump(dict_inputs, f, indent=4)
            
            list_widget = []
            dict_widget_paths[path] = {}
            for key, value in dict_inputs.items():

                w = mo.ui.number(
                    label=f"{key}:",
                    value=value,
                    on_change=set_state,
                )
                list_widget.append(w)
                dict_widget_paths[path][key] = w
            
            widget = mo.vstack(list_widget)
            widget_paths[path] = widget

        if path == "solver_settings.json":

            file_path = working_path / path
            if file_path.exists():
                with open(file_path) as f:
                    dict_inputs = json.load(f)
            else:
                dict_inputs = {
                    "dt": 1.0,
                    "scheme": "backward",
                    "solver": "direct",
                }
                with open(file_path, "w") as f:
                    json.dump(dict_inputs, f, indent=4)
            
            list_widget = []
            dict_widget_paths[path] = {}
            for key, value in dict_inputs.items():

                if type(value) == str:
                    w = mo.ui.text(
                        label=f"{key}:",
                        value=value,
                        on_change=set_state,
                    )
                else:
                    w = mo.ui.number(
                        label=f"{key}:",
                        step=1,
                        value=value,
                        on_change=set_state,
                    )
                list_widget.append(w)
                dict_widget_paths[path][key] = w
            
            widget = mo.vstack(list_widget)
            widget_paths[path] = widget
    
    return widget_paths, dict_widget_paths


def results(
    working_path: Path,
) -> dict:

    def _geometry_output(
        value: str,
    ) -> mo.Html:

        full_working_path = Path(os.path.split(value)[0])
        relative_path = full_working_path.relative_to(working_path)

        html_path = full_working_path / "html"
        if html_path.exists():
            for x3d_file in html_path.glob("*.x3d"):
                x3d_file.unlink()

        shape = TopoDS_Shape()
        builder = BRep_Builder()
        breptools.Read(shape, value, builder)

        if shape.ShapeType() == TopAbs_WIRE:
            shape = topods.Wire(shape)

        display = x3dom_renderer.X3DomRenderer()
        display.DisplayShape(
            shape=shape,
            export_edges=True,
        )
        display.generate_html_file(
            axes_plane=False,
            axes_plane_zoom_factor=2.0,
        )

        shutil.copytree(
            src=display._path,
            dst=html_path,
            dirs_exist_ok=True,
        )
        html_file = html_path / "index.html"
        html_file.write_text(
            data=re.sub(
                pattern=r"background\s*:\s*linear-gradient\([^)]+\)",
                repl="background: white",
                string=html_file.read_text(),
            )
        )

        result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/html/index.html" width="100%" height="500"></iframe>')

        return result

    def _mesh_output(
        value: str,
    ) -> mo.Html:
        
        full_working_path = Path(os.path.split(value)[0])
        relative_path = full_working_path.relative_to(working_path)

        mesh = pv.read(value) 
        plotter = pv.Plotter()
        plotter.add_mesh(
            mesh=mesh,
            color="#4cace6",
            show_edges=True,
            edge_color="black",
            specular=0.5,
        )
        plotter.export_html(
            filename=full_working_path / "mesh.html",
        )

        result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/mesh.html" width="100%" height="500"></iframe>')

        return result

    def _model_output(
        value: str,
    ) -> mo.ui.tabs:

        full_working_path = Path(os.path.split(value)[0])
        relative_path = full_working_path.relative_to(working_path)

        mesh:pv.UnstructuredGrid = pv.read(value)

        tabs = {}
        for label in ["Constraint", "Load"]:

            boundary = mesh.threshold(
                value=(1, 1),
                scalars=label,
                all_scalars=True,
            )

            plotter = pv.Plotter()
            plotter.add_mesh(
                mesh=mesh,
                color="white",
                culling="front",
                specular=0.3,
            )
            plotter.add_mesh(
                mesh=boundary,
                color="red",
                ambient=1.0,
                show_vertices=True,
            )
            plotter.view_xz()
            plotter.export_html(
                filename=full_working_path / f"{label.lower()}.html",
            )

            tabs[label] = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/{label.lower()}.html" width="100%" height="500"></iframe>')

        result = mo.ui.tabs(tabs)

        return result

    def _solution_output(
        value: str,
    ) -> mo.Html:

        full_working_path = Path(os.path.split(value)[0])
        relative_path = full_working_path.relative_to(working_path)

        mesh0 = pv.read(os.path.join(value, "dump", "solution0.vtu"))
        
        reader = pv.get_reader(os.path.join(value, "solution.pvd"))
        times = reader.time_values
        reader.set_active_time_point(len(times)-1)
        mesh: pv.UnstructuredGrid = reader.read()[0]

        plotter = pv.Plotter()
        plotter.add_mesh(
            mesh=mesh0,
            color="white",
            opacity=0.2,
        )
        plotter.add_mesh(
            mesh=mesh,
            cmap="viridis",
            clim=[0.0, 6.698],
            scalars=mesh.point_data["Displacement"][:, 2],
            scalar_bar_args={
                "title": "Z Displacement",
            },
        )
        plotter.view_xz()
        plotter.export_html(
            filename=full_working_path / "solution.html",
        )

        result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/solution.html" width="100%" height="500"></iframe>')

        return result

    def _deflection_output(
        value: str,
    ) -> mo.vstack:
        
        image = mo.image(
            src=value,
            width=700,
        )

        result = mo.vstack([
            mo.vstack([mo.md("    ")]),
            mo.vstack([mo.md("    ")]),
            mo.vstack([mo.md("    ")]),
            mo.vstack([mo.md("    ")]),
            mo.vstack([image], align="center"),
        ])

        return result

    def _overall_output(
        value: str,
    ) -> mo.vstack:

        if Path(value).exists():
            image = mo.image(
                src=value,
                width=1000,
            )
            result = mo.vstack([
                mo.vstack([mo.md("    ")]),
                mo.vstack([mo.md("    ")]),
                mo.vstack([mo.md("    ")]),
                mo.vstack([mo.md("    ")]),
                mo.vstack([image], align="center"),
            ])
        else:
            result = None

        return result

    def _errors_output(
        value: str,
    ) -> mo.vstack:

        if Path(value).exists():
            df = pd.read_csv(
                filepath_or_buffer=Path(value),
                index_col="ID",
            )
            df = df.rename(columns={
                "Error_Utip": "Error Utip (%)",
                "Error_Wtip": "Error Wtip (%)",
            })
            result = mo.vstack([
                mo.vstack([mo.md("    ")]),
                mo.vstack([mo.md("    ")]),
                mo.vstack([mo.md("    ")]),
                mo.vstack([mo.md("    ")]),
                mo.vstack([mo.md(df.to_html())]),
            ], align="center")
        else:
            result = None

        return result

    dict_results_builder = {
        "geometry.brep": _geometry_output,
        "mesh.msh": _mesh_output,
        "model.vtk": _model_output,
        "solution": _solution_output,
        "deflection.png": _deflection_output,
        "overall_comparisons.png": _overall_output,
        "overall_errors.csv": _errors_output,
    }

    return dict_results_builder