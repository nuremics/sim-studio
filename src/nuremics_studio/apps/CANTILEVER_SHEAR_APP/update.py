import json
from pathlib import Path


def studies_settings(
    working_path: Path,
    dict_widget_paths: dict,
) -> list:
    
    list_paths = []
    for path, widget in dict_widget_paths.items():
        
        if path == "mesh_settings.json":

            dict_inputs = {
                "elem": widget["elem"].value,
                "nb_elem_length": widget["nb_elem_length"].value,
                "nb_elem_width": widget["nb_elem_width"].value,
                "nb_elem_height": widget["nb_elem_height"].value,
            }
            file_path = working_path / path
            with open(file_path, "w") as f:
                json.dump(dict_inputs, f, indent=4)
            
            list_paths.append(path)

        if path == "solver_settings.json":

            dict_inputs = {
                "dt": widget["dt"].value,
                "ramp": widget["ramp"].value,
                "scheme": widget["scheme"].value,
                "solver": widget["solver"].value,
            }
            file_path = working_path / path
            with open(file_path, "w") as f:
                json.dump(dict_inputs, f, indent=4)
            
            list_paths.append(path)
    
    return list_paths