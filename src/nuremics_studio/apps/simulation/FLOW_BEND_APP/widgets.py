import json
import os
import re
import shutil
from pathlib import Path

import marimo as mo
import numpy as np
import pyvista as pv
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepTools import breptools
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.TopoDS import TopoDS_Shape, topods
from OCC.Display.WebGl import x3dom_renderer


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
            # transparency=0.9,
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

        # result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/html/index.html" width="100%" height="500"></iframe>')
        result = mo.Html(f'<iframe src="https://nuremics.github.io/use-cases/simulation/flow-bend/results/{relative_path}/html/index.html" width="100%" height="500"></iframe>')

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
            lighting=False,
        )
        plotter.view_xz()
        plotter.export_html(
            filename=full_working_path / "mesh.html",
        )

        # result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/mesh.html" width="100%" height="500"></iframe>')
        result = mo.Html(f'<iframe src="https://nuremics.github.io/use-cases/simulation/flow-bend/results/{relative_path}/mesh.html" width="100%" height="500"></iframe>')

        return result

    def _model_output(
        value: str,
    ) -> mo.ui.tabs:

        full_working_path = Path(os.path.split(value)[0])
        relative_path = full_working_path.relative_to(working_path)

        mesh: pv.UnstructuredGrid = pv.read(value)

        tabs = {}
        for label in ["Inlet", "Outlet", "Walls"]:

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

            # tabs[label] = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/{label.lower()}.html" width="100%" height="500"></iframe>')
            tabs[label] = mo.Html(f'<iframe src="https://nuremics.github.io/use-cases/simulation/flow-bend/results/{relative_path}/{label.lower()}.html" width="100%" height="500"></iframe>')

        result = mo.ui.tabs(tabs)

        return result

    def _solution_output(
        value: str,
    ) -> mo.Html:

        full_working_path = Path(os.path.split(value)[0])
        relative_path = full_working_path.relative_to(working_path)

        tabs = {}

        tabs["Animation"] = mo.video(
            src=os.path.join(value, "animation.mp4"),
            controls=True,
            autoplay=True,
            loop=True,
        )

        mesh0 = pv.read(os.path.join(value, "mesh.msh"))
        
        reader = pv.get_reader(os.path.join(value, "dump", "u.pvd"))
        times = reader.time_values
        reader.set_active_time_point(len(times) - 1)
        mesh: pv.UnstructuredGrid = reader.read()[0]

        slice = mesh.slice(
            normal=[0, 1, 0],
            origin=[0, 0, 0],
        )

        velocity_magnitude = np.linalg.norm(slice.point_data["u"], axis=1)

        plotter = pv.Plotter()
        plotter.add_mesh(
            mesh=mesh0,
            specular=0.3,
            color="white",
            culling="front",
        )
        plotter.add_mesh(
            mesh=slice,
            lighting=False,
            cmap="jet",
            scalars=velocity_magnitude,
            scalar_bar_args={
                "title": "u Magnitude",
            },
        )
        plotter.view_xz()
        plotter.export_html(
            filename=full_working_path / "solution.html",
        )

        # tabs["3D"] = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/solution.html" width="100%" height="500"></iframe>')
        tabs["3D"] = mo.Html(f'<iframe src="https://nuremics.github.io/use-cases/simulation/flow-bend/results/{relative_path}/solution.html" width="100%" height="500"></iframe>')

        result = mo.ui.tabs(tabs)

        return result

    def _probes_output(
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

    dict_results_builder = {
        "geometry.brep": _geometry_output,
        "mesh.msh": _mesh_output,
        "model.vtk": _model_output,
        "solution": _solution_output,
        "probes.png": _probes_output,
        # "overall_comparisons.png": _overall_output,
        # "overall_errors.csv": _errors_output,
    }

    return dict_results_builder