from pathlib import Path
from typing import Optional, Tuple

import marimo as mo
import pandas as pd
from nuremics import Application

import nuremics_studio.core.utils as utils


def app_banner(
    app_name: str,
    app_logo: str,
    app_color: str,
    app_link: str,
) -> mo.Html:

    if app_link is not None:
        wrapper_start = f'<a href="{app_link}" target="_blank" class="jost-banner-link">'
        wrapper_end = "</a>"
        banner_hover = ".jost-banner:hover { box-shadow: 0 0 20px rgba(0, 0, 0, 0.25); }"
    else:
        wrapper_start = ""
        wrapper_end = ""
        banner_hover = ""

    widget = mo.Html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;600&display=swap" rel="stylesheet">

        <style>
        .jost-banner-link {{
            text-decoration: none;
            display: block;
        }}

        .jost-banner {{
            display: flex;
            align-items: center;
            gap: 14px;

            font-family: 'Jost', sans-serif;
            color: white;
            font-size: 30px;
            font-weight: 600;

            background-color: {app_color};
            padding: 14px 20px;
            border-radius: 10px;

            box-shadow: 0 0 14px rgba(0, 0, 0, 0.25);

            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        {banner_hover}

        .jost-banner img {{
            height: 50px;
        }}
        </style>

        {wrapper_start}
        <div class="jost-banner">
            <img src="{app_logo}">
            <div>
                <strong> {app_name} </strong>
            </div>
        </div>
        {wrapper_end}
    """)

    return widget


def use_case(
    color: str,
    visual: str,
    use_case_link: str,
    use_case_title: str,
    use_case_description: str,
    dependencies: list,
) -> mo.Html:
    
    badge_imgs = []
    for url in dependencies:
        badge_imgs.append(f'<img src="{url}" />')
    card_badges = '<p class="badges">\n    ' + "\n    ".join(badge_imgs) + '\n</p>'
    
    all_elements = True
    if (visual is None) or \
       (use_case_title is None) or \
       (use_case_description is None):
        all_elements = False
    
    if all_elements:

        if use_case_link is not None:
            wrapper_start = f'<a href="{use_case_link}" target="_blank" class="image-card-link">'
            wrapper_end = "</a>"
            image_card_hover = ".image-card:hover { box-shadow: 0 0 20px rgba(0, 0, 0, 0.25); }"
        else:
            wrapper_start = ""
            wrapper_end = ""
            image_card_hover = ""

        html = mo.Html(f"""
            <link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;600&display=swap" rel="stylesheet">

            <style>
            .image-card-link {{
                text-decoration: none;
                display: inline-block;
            }}

            .image-card {{
                font-family: 'Jost', sans-serif;
                background-color: white;
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 0 14px rgba(0, 0, 0, 0.2);

                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}

            {image_card_hover}

            .image-card-title {{
                color: {color};
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 0px;
            }}
                        
            .image-card-description {{
                color: #7F7F7FFF;        
                font-size: 14px; 
                text-align: center;
                margin-bottom: 6px;
            }}

            .main-image {{
                width: 100%;
                display: block;
                margin: 0 auto;
                border-radius: 8px;
                margin-bottom: 12px;
            }}

            .badges {{
                display: flex;
                gap: 5px;
                justify-content: flex-start;
                flex-wrap: wrap;
            }}

            .badges img {{
                height: 20px;
                width: auto;
            }}
            
            </style>

            {wrapper_start}
            <div class="image-card">
                <div class="image-card-title">
                    {use_case_title}
                </div>
                <div class="image-card-description">
                    {use_case_description}
                </div>
                <img src="{visual}" class="main-image">
                {card_badges}
            </div>
            {wrapper_end}
        """)

        widget = mo.vstack([
            mo.vstack(["      "]),
            mo.vstack(["      "]),
            html,
            mo.vstack(["      "]),
            mo.vstack(["      "]),
            mo.vstack(["      "]),
            mo.vstack(["      "]),
        ])

    else:

        widget = mo.vstack([
            mo.vstack(["      "]),
            mo.vstack(["      "]),
            mo.vstack(["      "]),
        ])
    
    return widget


def working_dir(
    working_dir: str,
) -> mo.ui.text:
    
    widget = mo.ui.text(
        label="Working directory:",
        value=working_dir,
    )

    return widget


def splinecloud_config(
    app_config: str,
    set_state: mo.state,
) -> tuple[mo.Html, dict]:
    
    dict_widget = {}
    if app_config is not None:
        config_button = mo.ui.run_button(
            kind="neutral",
            label="Configure from SplineCloud",
            full_width=False,
            on_change=set_state,
        )
        image = mo.image(
            src="https://splinecloud.com/img/sc-logo.png",
            width=80,
        )
        widget = mo.vstack(
            [image, config_button],
            align="center", gap=0.75,
        )
        dict_widget["config_button"] = config_button
    else:
        widget = mo.vstack([
            mo.md("    "),
            mo.md("    ")
        ])
    
    return widget, dict_widget


def studies(
    list_studies: list[str],
) -> mo.ui.data_editor:
    
    if list_studies:
        df = pd.DataFrame({"Studies": list_studies})
    else:
        df = pd.DataFrame({"Studies": pd.Series(dtype=str)})
    
    widget = mo.ui.data_editor(df)

    return widget


def config(
    dict_studies: dict,
    set_state: mo.state,
) -> tuple[mo.ui.tabs, dict]:
    
    dict_widget = {}
    dict_tabs = {}
    for key, value in dict_studies["config"].items():

        list_wgt = []
        dict_widget[key] = {}

        execute_wgt = mo.ui.switch(
            label="execute",
            value=value["execute"],
            on_change=set_state,
        )
        list_wgt.append(mo.vstack([execute_wgt]))
        dict_widget[key]["execute"] = execute_wgt

        list_wgt.append(mo.md("**INPUT PARAMETERS**"))

        dict_user_params_wgt = {}
        for k, v in value["user_params"].items():
            if v is None:
                val = False
            else:
                val = v
            w = mo.ui.checkbox(
                label=k,
                value=val,
                on_change=set_state,
            )
            dict_user_params_wgt[k] = w
            list_wgt.append(w)

        dict_widget[key]["user_params"] = dict_user_params_wgt

        list_wgt.append(mo.md("**INPUT PATHS**"))

        dict_user_paths_wgt = {}
        for k, v in value["user_paths"].items():
            if v is None:
                val = False
            else:
                val = v
            w = mo.ui.checkbox(
                label=k,
                value=val,
                on_change=set_state,
            )
            dict_user_paths_wgt[k] = w
            list_wgt.append(w)

        dict_widget[key]["user_paths"] = dict_user_paths_wgt

        tab = mo.vstack(list_wgt)
        dict_tabs[key] = tab

    widget = mo.ui.tabs(
        tabs=dict_tabs,
    )

    return widget, dict_widget


def datasets(
    app: Application,
    working_path: Path,
    list_studies: list[str],
    set_state: mo.state,
) -> Tuple[Optional[mo.ui.data_editor], dict[str, Optional[mo.ui.data_editor]]]:
    
    cols = {}
    for study in list_studies:
        df_inputs = utils.get_inputs_csv(
            app=app,
            working_path=working_path,
            study=study,
        )
        if df_inputs is not None:
            cols[study] = df_inputs["ID"].astype(str)
    
    df_datasets = pd.DataFrame(cols)
    df_datasets = df_datasets.fillna("")
    
    if df_datasets.shape[1] != 0:
        widget = mo.ui.data_editor(
            data=df_datasets,
            on_change=set_state,
        )
    else:
        widget = None
    
    dict_widget = {"datasets": widget}

    return widget, dict_widget


def settings(
    app: Application,
    default_params: dict,
    working_path: Path,
    list_studies: list[str],
    set_state: mo.state,
) -> tuple[mo.ui.tabs, dict]:
    
    app_category = app.workflow.app_category
    app_name = app.workflow.app_name
    module_path = f"nuremics_studio.apps.{app_category}.{app_name}.widgets"
    module = utils.load_module(
        module_path=module_path,
    )
    if module is not None:
        func = utils.get_function(
            func_name="settings",
            module=module,
        )
    else:
        func = None

    dict_widget = {}
    dict_tabs = {}
    for study in list_studies:

        dict_widget[study] = {}
        dict_tab = {}

        # -------------- #
        # Procs settings #
        # -------------- #
        dict_widget[study]["Procs"] = {}
        dict_procs_wgt = {}

        dict_procs = utils.get_json_file(
            working_path=working_path,
            study=study,
            file_prefix="process",
        )
        for key, value in dict_procs.items():
            
            dict_widget[study]["Procs"][key] = {}
            list_procs_wgt = []

            execute_wgt = mo.ui.switch(
                label="execute",
                value=value["execute"],
                on_change=set_state,
            )
            dict_widget[study]["Procs"][key]["execute"] = execute_wgt
            list_procs_wgt.append(execute_wgt)

            silent_wgt = mo.ui.switch(
                label="silent mode",
                value=value["silent"],
                on_change=set_state,
            )
            dict_widget[study]["Procs"][key]["silent"] = silent_wgt
            list_procs_wgt.append(silent_wgt)

            dict_procs_wgt[key] = mo.vstack(list_procs_wgt)

        # ------------ #
        # Fixed inputs #
        # ------------ #
        dict_widget[study]["Fixed"] = {}
        dict_widget[study]["Fixed"]["params"] = {}
        dict_widget[study]["Fixed"]["paths"] = {}

        dict_inputs: dict = utils.get_json_file(
            working_path=working_path,
            study=study,
            file_prefix="inputs",
        )
        
        if app.workflow.fixed_params[study] or app.workflow.fixed_paths[study]:
            
            dict_tab["Fixed"] = {}
            list_fixed_params_wgt = []
            list_fixed_paths_wgt = []

            # Fixed params
            if app.workflow.fixed_params[study]:
                list_fixed_params_wgt.append(mo.md("**INPUT PARAMETERS**"))

            for param in app.workflow.fixed_params[study]:

                if (dict_inputs[param] is None) and (param in default_params):
                    value = default_params[param]
                else:
                    value = dict_inputs[param]

                if app.workflow.params_type[param][1] == "float":
                    w = mo.ui.number(
                        label=f"{param}:",
                        value=value,
                        on_change=set_state,
                    )

                elif app.workflow.params_type[param][1] == "int":
                    w = mo.ui.number(
                        label=f"{param}:",
                        value=value,
                        step=1,
                        on_change=set_state,
                    )

                elif app.workflow.params_type[param][1] == "bool":
                    if value is None:
                        val = False
                    else:
                        val = value
                    w = mo.ui.checkbox(
                        label=param,
                        value=val,
                        on_change=set_state,
                    )

                elif app.workflow.params_type[param][1] == "str":
                    if value is None:
                        val = ""
                    else:
                        val = value
                    w = mo.ui.text(
                        label=f"{param}:",
                        value=val,
                        on_change=set_state,
                    )
                
                dict_widget[study]["Fixed"]["params"][param] = w
                list_fixed_params_wgt.append(w)

            # Fixed paths
            if app.workflow.fixed_paths[study]:
                list_fixed_paths_wgt.append(mo.md("**INPUT PATHS**"))

            widget_fixed_paths = {}
            dict_widget_fixed_paths = {}
            if func is not None:
                widget_fixed_paths, dict_widget_fixed_paths = func(
                    working_path=working_path / f"{study}/0_inputs",
                    list_paths=app.workflow.fixed_paths[study],
                    set_state=set_state,
                )

            for path in app.workflow.fixed_paths[study]:

                if path in widget_fixed_paths:
                    dict_widget[study]["Fixed"]["paths"][path] = dict_widget_fixed_paths[path]
                    continue
                
                if dict_inputs[path] is None:
                    val = ""
                else:
                    val = dict_inputs[path]

                w = mo.ui.text(
                    label=f"{path}:",
                    value=val,
                    on_change=set_state,
                )
                dict_widget[study]["Fixed"]["paths"][path] = w
                w = mo.hstack(
                    [w, mo.md(f"`{working_path / f'{study}/0_inputs'}`")],
                    justify="start",
                    align="center",
                )
                list_fixed_paths_wgt.append(w)

            list_fixed_wgt = []
            if list_fixed_params_wgt:
                list_fixed_wgt.append(mo.vstack([mo.md("    ")]))
                list_fixed_wgt.append(mo.vstack(list_fixed_params_wgt))
            if list_fixed_paths_wgt:
                list_fixed_wgt.append(mo.vstack([mo.md("    ")]))
                list_fixed_wgt.append(mo.vstack(list_fixed_paths_wgt))
            if widget_fixed_paths:
                list_fixed_wgt.append(mo.ui.tabs(tabs=widget_fixed_paths))

            dict_tab["Fixed"] = mo.vstack(list_fixed_wgt)

        # --------------- #
        # Variable inputs #
        # --------------- #
        dict_widget[study]["Variable"] = {}

        df_inputs = utils.get_inputs_csv(
            app=app,
            working_path=working_path,
            study=study,
        )
        if df_inputs is not None:

            dict_tab["Variable"] = {}
            dict_accordion_datasets = {}

            for dataset in df_inputs["ID"]:

                dict_widget[study]["Variable"][dataset] = {}
                dict_widget[study]["Variable"][dataset]["params"] = {}
                dict_widget[study]["Variable"][dataset]["paths"] = {}

                list_variable_params_wgt = []
                list_variable_paths_wgt = []

                execute_wgt = mo.ui.switch(
                    label="execute",
                    value=bool(df_inputs.loc[df_inputs["ID"] == dataset, "EXECUTE"].values[0]),
                    on_change=set_state,
                )
                dict_widget[study]["Variable"][dataset]["execute"] = execute_wgt
            
                # Variable params
                if app.workflow.variable_params[study]:
                    list_variable_params_wgt.append(mo.md("**INPUT PARAMETERS**"))

                for param in app.workflow.variable_params[study]:
                    
                    val_param = df_inputs.loc[df_inputs["ID"] == dataset, param].values[0]
                    if (pd.isna(val_param)):
                        if param in default_params:
                            val_param = default_params[param]
                        else:
                            val_param = None

                    if app.workflow.params_type[param][1] == "float":
                        if val_param is not None:
                            val_param = float(val_param)
                        w = mo.ui.number(
                            label=f"{param}:",
                            value=val_param,
                            on_change=set_state,
                        )

                    elif app.workflow.params_type[param][1] == "int":
                        if val_param is not None:
                            val_param = int(val_param)
                        w = mo.ui.number(
                            label=f"{param}:",
                            value=val_param,
                            step=1,
                            on_change=set_state,
                        )

                    elif app.workflow.params_type[param][1] == "bool":
                        if val_param is None:
                            val = False
                        else:
                            val = bool(val_param)
                        w = mo.ui.checkbox(
                            label=param,
                            value=val,
                            on_change=set_state,
                        )

                    elif app.workflow.params_type[param][1] == "str":
                        if val_param is None:
                            val = ""
                        else:
                            val = str(val_param)
                        w = mo.ui.text(
                            label=f"{param}:",
                            value=val,
                            on_change=set_state,
                        )
                    
                    dict_widget[study]["Variable"][dataset]["params"][param] = w
                    list_variable_params_wgt.append(w)

                # Variable paths
                if app.workflow.variable_paths[study]:
                    list_variable_paths_wgt.append(mo.md("**INPUT PATHS**"))

                widget_variable_paths = {}
                dict_widget_variable_paths = {}
                if func is not None:
                    widget_variable_paths, dict_widget_variable_paths = func(
                        working_path=working_path / f"{study}/0_inputs/0_datasets/{dataset}",
                        list_paths=app.workflow.variable_paths[study],
                        set_state=set_state,
                    )

                for path in app.workflow.variable_paths[study]:

                    if path in widget_variable_paths:
                        dict_widget[study]["Variable"][dataset]["paths"][path] = dict_widget_variable_paths[path]
                        continue
                    
                    if dict_inputs[path][dataset] is None:
                        val = ""
                    else:
                        val = dict_inputs[path][dataset]

                    w = mo.ui.text(
                        label=f"{path}:",
                        value=val,
                        on_change=set_state,
                    )
                    dict_widget[study]["Variable"][dataset]["paths"][path] = w
                    w = mo.hstack(
                        [w, mo.md(f"`{working_path / f'{study}/0_inputs/0_datasets/{dataset}'}`")],
                        justify="start",
                        align="center",
                    )
                    list_variable_paths_wgt.append(w)

                list_variable_wgt = []
                list_variable_wgt.append(mo.vstack([mo.md("    ")]))
                list_variable_wgt.append(mo.vstack([execute_wgt]))
                if list_variable_params_wgt:
                    list_variable_wgt.append(mo.vstack([mo.md("    ")]))
                    list_variable_wgt.append(mo.vstack(list_variable_params_wgt))
                if list_variable_paths_wgt:
                    list_variable_wgt.append(mo.vstack([mo.md("    ")]))
                    list_variable_wgt.append(mo.vstack(list_variable_paths_wgt))
                if widget_variable_paths:
                    list_variable_wgt.append(mo.ui.tabs(tabs=widget_variable_paths))

                dict_accordion_datasets[dataset] = mo.vstack(list_variable_wgt)

            dict_tab["Variable"] = mo.vstack([
                    mo.accordion(
                        items=dict_accordion_datasets,
                    ),
                ])

        dict_tabs[study] = mo.vstack([
            mo.vstack([mo.accordion(items=dict_procs_wgt)]),
            mo.vstack([mo.ui.tabs(tabs=dict_tab)]),
        ])

    widget = mo.ui.tabs(
        tabs=dict_tabs,
    )

    return widget, dict_widget


def analysis(
    working_path: Path,
    list_studies: list,
    set_state: mo.state,
) -> tuple[mo.ui.tabs, dict]:
    
    dict_widget = {}
    dict_studies_settings = {}
    for study in list_studies:

        dict_widget[study] = {}

        dict_analysis: dict = utils.get_json_file(
            working_path=working_path,
            study=study,
            file_prefix="analysis",
        )

        dict_settings = {}
        for proc, value in dict_analysis.items():
            if value and next(iter(value.values())):
                
                dict_widget[study][proc] = {}
                dict_settings_dataset = {}
                for dataset, settings in value.items():
                    
                    list_widgets = []
                    dict_widget[study][proc][dataset] = {}
                    for k, v in settings.items():

                        if isinstance(v, str):
                            w = mo.ui.text(
                                label=f"{k}:",
                                value=v,
                                on_change=set_state,
                            )
                    
                        elif isinstance(v, bool):
                            w = mo.ui.checkbox(
                                label=k,
                                value=v,
                                on_change=set_state,
                            )
                    
                        elif isinstance(v, int):
                            w = mo.ui.number(
                                label=f"{k}:",
                                value=v,
                                step=1,
                                on_change=set_state,
                            )
                    
                        elif isinstance(v, float):
                            w = mo.ui.number(
                                label=f"{k}:",
                                value=v,
                                on_change=set_state,
                            )
                        
                        list_widgets.append(w)
                        dict_widget[study][proc][dataset][k] = w

                    dict_settings_dataset[dataset] = mo.vstack(list_widgets)
                dict_settings[proc] = mo.accordion(dict_settings_dataset)
        
        dict_studies_settings[study] = mo.ui.tabs(dict_settings)
    widget = mo.ui.tabs(dict_studies_settings)

    return widget, dict_widget


def results(
    app: Application,
    working_path: Path,
    list_studies: list,
) -> Optional[mo.ui.tabs]:
    
    app_category = app.workflow.app_category
    app_name = app.workflow.app_name
    module_path = f"nuremics_studio.apps.{app_category}.{app_name}.widgets"
    module = utils.load_module(
        module_path=module_path,
    )
    if module is not None:
        func = utils.get_function(
            func_name="results",
            module=module,
        )
    else:
        func = None

    if func is not None:

        dict_results_builder = func(
            working_path=working_path,
        )
        dict_studies_results = {}
        for study in list_studies:

            dict_paths: dict = utils.get_json_file(
                working_path=working_path,
                study=study,
                file_prefix=".paths",
            )

            dict_results = {}
            for result_key, builder in dict_results_builder.items():

                if isinstance(dict_paths[result_key], dict):
                    result = {}
                    for key, value in dict_paths[result_key].items():
                        result[key] = builder(value)
                    all_results = mo.accordion(result)

                else:
                    if builder(dict_paths[result_key]) is not None: 
                        all_results = builder(dict_paths[result_key])
                    else:
                        continue

                dict_results[result_key] = all_results
            dict_studies_results[study] = mo.ui.tabs(dict_results)
        widget = mo.ui.tabs(dict_studies_results)
    
    else:
        widget = None
    
    return widget