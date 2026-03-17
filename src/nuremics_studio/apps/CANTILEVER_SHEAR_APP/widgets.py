import os
import json
import re
import shutil
from pathlib import Path

import marimo as mo
import pyvista as pv
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepTools import breptools
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import topods
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.TopAbs import TopAbs_SOLID
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.TopExp import TopExp_Explorer
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
                    dict_mesh_settings = json.load(f)
            else:
                dict_mesh_settings = {
                    "elem": "hexa",
                    "nb_elem_length": 16,
                    "nb_elem_width": 1,
                    "nb_elem_height": 1,
                }
                with open(file_path, "w") as f:
                    json.dump(dict_mesh_settings, f, indent=4)
            
            list_widget = []
            dict_widget_paths[path] = {}
            for key, value in dict_mesh_settings.items():

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

    def _geometry_result(
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

        # import pyvista as pv
        # mesh = pv.Sphere() 
        # plotter = pv.Plotter()
        # plotter.add_mesh(mesh, color="orange")
        # plotter.export_html(
        #     filename=full_working_path / "sphere.html",
        # )

        result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/html/index.html" width="100%" height="500"></iframe>')
        # result = mo.Html(f'<iframe src="https://nuremics.github.io/use-cases/simulation/cantilever-shear/results/{relative_path}/html/index.html" width="100%" height="500"></iframe>')

        return result

    def _labeling_result(
        value: str,
    ) -> mo.Html:
        
        with open(value) as f:
            dict_labels = json.load(f)

        full_working_path = Path(os.path.split(value)[0])
        relative_path = full_working_path.relative_to(working_path)

        tabs = {}
        for label in ["Constraint", "Load"]:

            label_dir = full_working_path / label
            label_dir.mkdir(
                exist_ok=True,
                parents=True,
            )

            dim = dict_labels["entities"][label]["dim"]
            ids = dict_labels["entities"][label]["ids"]

            html_path = label_dir / "html"
            if html_path.exists():
                for x3d_file in html_path.glob("*.x3d"):
                    x3d_file.unlink()

            shape = TopoDS_Shape()
            builder = BRep_Builder()
            breptools.Read(shape, dict_labels["geometry"], builder)

            if shape.ShapeType() == TopAbs_WIRE:
                shape = topods.Wire(shape)

            display = x3dom_renderer.X3DomRenderer()
            display.DisplayShape(
                shape=shape,
                transparency=0.9,
            )

            if dim == 3:
                exp = TopExp_Explorer(shape, TopAbs_SOLID)
            elif dim == 2:
                exp = TopExp_Explorer(shape, TopAbs_FACE)
            elif dim == 1:
                exp = TopExp_Explorer(shape, TopAbs_EDGE)
            elif dim == 0:
                exp = TopExp_Explorer(shape, TopAbs_VERTEX)
            
            index = 1
            while exp.More():
                entity = exp.Current()
                if index in ids:
                    display.DisplayShape(
                        shape=entity,
                        export_edges=True,
                        color=(1.0, 0.0, 0.0),
                        transparency=0.0,
                    )
                exp.Next()
                index += 1

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

            tabs[label] = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/{label}/html/index.html" width="100%" height="500"></iframe>')
            # tabs[label] = mo.Html(f'<iframe src="https://nuremics.github.io/use-cases/simulation/cantilever-shear/results/{relative_path}/{label}/html/index.html" width="100%" height="500"></iframe>')

        result = mo.ui.tabs(tabs)

        return result

    def _mesh_result(
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
        # result = mo.Html(f'<iframe src="https://nuremics.github.io/use-cases/simulation/cantilever-shear/results/{relative_path}/mesh.html" width="100%" height="500"></iframe>')

        return result

    dict_results_builder = {
        "geometry.brep": _geometry_result,
        "labels.json": _labeling_result,
        "mesh.msh": _mesh_result,
    }

    return dict_results_builder