import base64
import http.server
import importlib
import json
import os
import socketserver
import threading
from functools import partial
from importlib.resources import files
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Optional, Union

import pandas as pd
import yaml
from nuremics import Application
from platformdirs import user_config_path

CONFIG_PATH = user_config_path(
    appname="nuRemics",
    appauthor=False,
)
SETTINGS_FILE: Path = CONFIG_PATH / "settings.json"

_httpd_server = None


def image_to_data_url(
    path: Union[str, os.PathLike],
) -> str:
    
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def get_app_features(
    app_name: str,
) -> dict[str, None]:

    features_file = files("nuremics_studio.resources").joinpath("features.yml")
    with open(features_file) as f:
        dict_features = yaml.safe_load(f)

    app_features = {
        "logo": None,
        "color": None,
        "dependencies": None,
        "import": None,
        "visual": None,
        "app_link": None,
        "use_case_link": None,
        "use_case_title": None,
        "use_case_description": None,
        "config": None,
    }
    app_features.update(dict_features["apps"][app_name])

    if app_features["logo"] is None:
        app_features["logo"] = dict_features["common"]["logo"]
    if app_features["color"] is None:
        app_features["color"] = dict_features["common"]["color"]

    common_deps = dict_features["common"]["dependencies"]
    app_deps = app_features["dependencies"]
    app_features["dependencies"] = common_deps + app_deps
    
    if os.path.split(app_features["logo"])[0] == "":
        app_features["logo"] = image_to_data_url(
            files("nuremics_studio.resources").joinpath(app_features["logo"]),
        )

    return app_features


def load_local_server(
    working_path: Path,
) -> None:
    
    global _httpd_server
    
    PORT = 8000

    if _httpd_server is not None:
        _httpd_server.shutdown()
        _httpd_server.server_close()
        _httpd_server = None

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(working_path))

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), handler)

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    _httpd_server = httpd


def load_module(
    module_path: str
) -> ModuleType:

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        module = None

    return module


def get_function(
    module: ModuleType,
    func_name: str
) -> Optional[Callable[..., Any]]:
    
    if hasattr(module, func_name):
        func = getattr(module, func_name)
    else:
        func = None
    
    return func


def get_settings() -> dict:
    
    with open(SETTINGS_FILE) as f:
        dict_settings = json.load(f)
    
    return dict_settings


def update_settings(
    dict_settings: dict
) -> None:
    
    with open(SETTINGS_FILE, "w") as f:
        json.dump(dict_settings, f, indent=4)


def get_studies(
    working_path: Path,
) -> dict:
    
    studies_file: Path = working_path / "studies.json"
    with open(studies_file) as f:
        dict_studies = json.load(f)
    
    return dict_studies


def update_studies(
    working_path: Path,
    dict_studies: dict,
) -> None:
    
    studies_file: Path = working_path / "studies.json"
    with open(studies_file, "w") as f:
        json.dump(dict_studies, f, indent=4)


def update_list_studies(
    working_path: Path,
    list_studies: list,
) -> None:
    
    studies_file: Path = working_path / "studies.json"
    with open(studies_file) as f:
        dict_studies = json.load(f)

    dict_studies["studies"] = list_studies
    with open(studies_file, "w") as f:
        json.dump(dict_studies, f, indent=4)


def get_json_file(
    working_path: Path,
    study: str,
    file_prefix: str,
) -> Optional[dict]:
    
    file_path: Path = working_path / f"{study}/{file_prefix}.json"
    if file_path.exists():
        with open(file_path) as f:
            dict = json.load(f)
    else:
        dict = None
    
    return dict


def update_json_file(
    dict: dict,
    working_path: Path,
    study: str,
    file_prefix: str,
) -> None:
    
    file_path: Path = working_path / f"{study}/{file_prefix}.json"
    with open(file_path, "w") as f:
        json.dump(dict, f, indent=4)


def get_inputs_csv(
    app: Application,
    working_path: Path,
    study: str,
) -> Optional[pd.DataFrame]:
    
    inputs_file: Path = working_path / f"{study}/inputs.csv"
    
    if inputs_file.exists():
        df_inputs_col = pd.read_csv(inputs_file, nrows=0)
        
        dtypes = {
            "ID": "string",
            "EXECUTE": "Int64",
        }
        for col in df_inputs_col.columns[1:-1]:
            if app.workflow.params_type[col][1] == "int":
                dtypes[col] = "Int64"
            if app.workflow.params_type[col][1] == "float":
                dtypes[col] = "float64"
            if app.workflow.params_type[col][1] == "bool":
                dtypes[col] = "boolean"
            if app.workflow.params_type[col][1] == "str":
                dtypes[col] = "string"
        
        df_inputs = pd.read_csv(
            filepath_or_buffer=inputs_file,
            dtype=dtypes,
        )
    
    else:
        df_inputs = None

    return df_inputs


def update_inputs_csv(
    df_inputs: pd.DataFrame,
    working_path: Path,
    study: str, 
) -> None:
    
    inputs_file: Path = working_path / f"{study}/inputs.csv"
    df_inputs.to_csv(
        path_or_buf=inputs_file,
        index=False,
    )