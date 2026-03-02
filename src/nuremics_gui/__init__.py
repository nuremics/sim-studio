from importlib.resources import files

def get_notebook():
    return files("nuremics_gui") / "nuRemics_App.py"