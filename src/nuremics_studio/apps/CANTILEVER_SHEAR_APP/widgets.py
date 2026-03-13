import os
import json
import shutil
from pathlib import Path

import marimo as mo
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

        # import pyvista as pv
        # mesh = pv.Sphere() 
        # plotter = pv.Plotter()
        # plotter.add_mesh(mesh, color="orange")
        # plotter.export_html(
        #     filename=full_working_path / "sphere.html",
        # )

        # result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/sphere.html" width="100%" height="600"></iframe>')
        result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/html/index.html" width="100%" height="600"></iframe>')
        # result = mo.Html(f'<iframe src="https://nuremics.github.io/use-cases/simulation/cantilever-shear/results/{relative_path}/html/index.html" width="100%" height="600"></iframe>')

        return result

    def _labeling_result(
        value: str,
    ) -> mo.Html:
        
        with open(value) as f:
            dict_labels = json.load(f)

        full_working_path = Path(os.path.split(value)[0])
        relative_path = full_working_path.relative_to(working_path)

        for label in ["Constraint"]:

            label_dir = full_working_path / "Constraint"
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

            result = mo.Html(f'<iframe src="http://localhost:8000/{relative_path}/{label}/html/index.html" width="100%" height="600"></iframe>')
        
        return result

    dict_results_builder = {
        "geometry.brep": _geometry_result,
        "labels.json": _labeling_result,
    }

    return dict_results_builder