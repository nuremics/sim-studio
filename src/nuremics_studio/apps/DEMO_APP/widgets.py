import json
import os
from pathlib import Path

import marimo as mo


def settings(
    working_path: Path,
    list_paths: list,
    set_state: mo.state,
) -> tuple[dict, dict]:
    
    widget_paths = {}
    dict_widget_paths = {}
    for path in list_paths:

        if path == "plot_title.txt":

            file_path = working_path / path
            if file_path.exists():
                with open(file_path) as f:
                    value = f.read()
            else:
                value = "2D polygon shape"
                with open(file_path, "w") as f:
                    f.write(value)
            
            widget = mo.ui.text(
                label="text:",
                value=value,
                on_change=set_state,
            )
            widget_paths[path] = widget
            dict_widget_paths[path] = widget

        if path == "velocity.json":

            file_path = working_path / path
            if file_path.exists():
                with open(file_path) as f:
                    dict_velocity = json.load(f)
            else:
                dict_velocity = {
                    "v0": 15.0,
                    "angle": 45.0,
                }
                with open(file_path, "w") as f:
                    json.dump(dict_velocity, f, indent=4)
            
            list_widget = []
            dict_widget_paths[path] = {}
            for key, value in dict_velocity.items():

                w = mo.ui.number(
                    label=f"{key}:",
                    value=value,
                    on_change=set_state,
                )
                list_widget.append(w)
                dict_widget_paths[path][key] = w
            
            widget = mo.vstack(list_widget)
            widget_paths[path] = widget
        
        if path == "configs":

            dict_tabs_files = {}

            folder_path = working_path / path
            if folder_path.exists():
                with open(folder_path / "display_config.json") as f:
                    dict_display = json.load(f)
                with open(folder_path / "solver_config.json") as f:
                    dict_solver = json.load(f)
            else:
                folder_path.mkdir(exist_ok=True, parents=True)
                
                dict_display = {
                    "fps": 60,
                    "size": 700,
                }
                with open(folder_path / "display_config.json", "w") as f:
                    json.dump(dict_display, f, indent=4)
                
                dict_solver = {
                    "timestep": 0.01,
                }
                with open(folder_path / "solver_config.json", "w") as f:
                    json.dump(dict_solver, f, indent=4)

            list_widget = []
            dict_widget_paths[path] = {}
            for key, value in dict_display.items():
                
                w = mo.ui.number(
                    label=f"{key}:",
                    value=value,
                    step=1,
                    on_change=set_state,
                )
                list_widget.append(w)
                dict_widget_paths[path][key] = w
            
            dict_tabs_files["display_config.json"] = mo.vstack(list_widget)

            list_widget = []
            for key, value in dict_solver.items():

                w = mo.ui.number(
                    label=f"{key}:",
                    value=value,
                    on_change=set_state,
                )
                list_widget.append(w)
                dict_widget_paths[path][key] = w
            
            dict_tabs_files["solver_config.json"] = mo.vstack(list_widget)

            widget = mo.ui.tabs(tabs=dict_tabs_files)
            widget_paths[path] = widget
    
    return widget_paths, dict_widget_paths


def results(**kwargs: object) -> dict:

    def _shape_result(
        value: str,
    ) -> mo.Html:
        
        image = mo.image(
            src=value,
            width=600,
        )
        return mo.vstack([mo.vstack([image], align="center")])
    
    def _comparison_result(
        value: str,
    ) -> mo.ui.tabs:
        
        image = mo.image(
            src=os.path.join(value, "model_vs_theory.png"),
            width=600,
        )
        tabs = mo.ui.tabs(
            tabs={
                "model_vs_theory.png": mo.vstack([mo.vstack([image], align="center")])
            }
        )
        return tabs

    def _overall_result(
        value: str,
    ) -> mo.Html:

        if Path(value).exists():
            image = mo.image(
                src=value,
                width=600,
            )
            result = mo.vstack([mo.vstack([image], align="center")])
        else:
            result = None
        
        return result

    dict_results_builder = {
        "polygon_shape.png": _shape_result,
        "comparison": _comparison_result,
        "overall_comparisons.png": _overall_result,
    }

    return dict_results_builder