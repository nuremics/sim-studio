import json
from pathlib import Path


def studies_settings(
    working_path: Path,
    dict_widget_paths: dict,
) -> list:
    
    list_paths = []
    for path, widget in dict_widget_paths.items():

        if path == "plot_title.txt":

            file_path = working_path / path
            with open(file_path, "w") as f:
                f.write(widget.value)
            
            list_paths.append(path)
        
        if path == "velocity.json":

            dict_velocity = {
                "v0": float(widget["v0"].value),
                "angle": float(widget["angle"].value),
            }
            file_path = working_path / path
            with open(file_path, "w") as f:
                json.dump(dict_velocity, f, indent=4)
            
            list_paths.append(path)
        
        if path == "configs":

            dict_display = {
                "fps": widget["fps"].value,
                "size": widget["size"].value,
            }
            dict_solver = {
                "timestep": float(widget["timestep"].value),
            }
            folder_path = working_path / path
            with open(folder_path / "display_config.json", "w") as f:
                json.dump(dict_display, f, indent=4)
            with open(folder_path / "solver_config.json", "w") as f:
                json.dump(dict_solver, f, indent=4)
            
            list_paths.append(path)
    
    return list_paths