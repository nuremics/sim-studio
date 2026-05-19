import json
import os
import re
import glob
import shutil
from pathlib import Path

import marimo as mo
import numpy as np
import pyvista as pv
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepTools import breptools
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import TopoDS_Shape
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

    def _labeling_output(
        value: str,
    ) -> mo.Html:

        full_working_path = Path(os.path.split(value)[0])
        relative_path = full_working_path.relative_to(working_path)

        with open(value) as f:
            dict_labels = json.load(f)

        shape = TopoDS_Shape()
        builder = BRep_Builder()
        breptools.Read(shape, dict_labels["geometry"], builder)

        tabs = {}
        for label in ["Inlet", "Outlet", "Walls"]:

            label_path = full_working_path / label
            if label_path.exists():
                shutil.rmtree(label_path)

            html_path = label_path / "html"

            display = x3dom_renderer.X3DomRenderer()
            display.DisplayShape(
                shape=shape,
                transparency=0.9,
            )

            index = 1
            exp = TopExp_Explorer(shape, TopAbs_FACE)
            while exp.More():
                entity = exp.Current()
                if index in dict_labels["entities"][label]["ids"]:
                    display.DisplayShape(
                        shape=entity,
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

        result = mo.ui.tabs(tabs)

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

        result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/mesh.html" width="100%" height="500"></iframe>')

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

        def _extract_number(filename: str) -> int:
            match = re.search(r'solution(\d+)\.vtu$', filename)
            return int(match.group(1)) if match else -1

        results = glob.glob(os.path.join(value, "dump", "u*.pvtu"))
        results = sorted(results, key=_extract_number)

        mesh0 = pv.read(os.path.join(value, "mesh.msh"))
        mesh = pv.read(results[-1])

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

        tabs["3D"] = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/solution.html" width="100%" height="500"></iframe>')

        result = mo.ui.tabs(tabs)

        return result

    def _plots_output(
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

    dict_results_builder = {
        "geometry.brep": _geometry_output,
        "labels.json": _labeling_output,
        "mesh.msh": _mesh_output,
        "solution": _solution_output,
        "probes.png": _plots_output,
        "profiles.png": _plots_output,
        "overall_comparisons.png": _overall_output,
    }

    return dict_results_builder