import copy
from pathlib import Path

from nuremics import Application

import nuremics_studio.core.utils as utils


def dict_studies(
    dict_studies: dict,
    dict_config_wgt: dict,
) -> dict:
    
    dict_studies_configured = copy.deepcopy(dict_studies)
    for key, value in dict_studies["config"].items():

        dict_studies_configured["config"][key]["execute"] = dict_config_wgt[key]["execute"].value
        
        for k, _ in value["user_params"].items():
            dict_studies_configured["config"][key]["user_params"][k] = dict_config_wgt[key]["user_params"][k].value
        for k, _ in value["user_paths"].items():
            dict_studies_configured["config"][key]["user_paths"][k] = dict_config_wgt[key]["user_paths"][k].value

    return dict_studies_configured


def datasets(
    app: Application,
    dict_datasets_wgt: dict,
    working_path: Path,
) -> None:
    
    datasets = dict_datasets_wgt["datasets"]
    if datasets is not None:
        for col in datasets.value.columns:
            
            df_inputs = utils.get_inputs_csv(
                app=app,
                working_path=working_path,
                study=col,
            )
            
            list_datasets = [x for x in datasets.value[col].to_list() if x]
            for dataset in list_datasets:
                if dataset not in df_inputs["ID"].values:
                    df_inputs.loc[len(df_inputs), "ID"] = dataset

            df_inputs = df_inputs[df_inputs["ID"].isin(list_datasets)]

            utils.update_inputs_csv(
                df_inputs=df_inputs,
                working_path=working_path,
                study=col,
            )


def studies_settings(
    app: Application,
    dict_settings_wgt: dict,
    working_path: Path,
) -> None:
    
    app_category = app.workflow.app_category
    app_name = app.workflow.app_name
    module_path = f"nuremics_studio.apps.{app_category}.{app_name}.update"
    module = utils.load_module(
        module_path=module_path,
    )
    if module is not None:
        func = utils.get_function(
            func_name="studies_settings",
            module=module,
        )
    else:
        func = None
    
    for key, value in dict_settings_wgt.items():

        # -------------- #
        # Procs settings #
        # -------------- #
        dict_procs: dict = utils.get_json_file(
            working_path=working_path,
            study=key,
            file_prefix="process",
        )
        for k, v in dict_procs.items():
            dict_procs[k]["execute"] = value["Procs"][k]["execute"].value
            dict_procs[k]["silent"] = value["Procs"][k]["silent"].value
        
        utils.update_json_file(
            dict=dict_procs,
            working_path=working_path,
            study=key,
            file_prefix="process",
        )
        
        # ------------ #
        # Fixed inputs #
        # ------------ #
        dict_inputs = utils.get_json_file(
            working_path=working_path,
            study=key,
            file_prefix="inputs",
        )

        # Fixed params
        for k, v in value["Fixed"]["params"].items():
            if (app.workflow.params_type[k][1] == "float") and (v.value is not None):
                dict_inputs[k] = float(v.value)
            else:
                dict_inputs[k] = v.value

        # Fixed paths
        list_fixed_paths = []
        if func is not None:
            list_fixed_paths = func(
                working_path=working_path / f"{key}/0_inputs",
                dict_widget_paths=value["Fixed"]["paths"],
            )

        for k, v in value["Fixed"]["paths"].items():
            if k not in list_fixed_paths:
                if v.value.strip() != "":
                    dict_inputs[k] = v.value
                else:
                    dict_inputs[k] = None
        
        # --------------- #
        # Variable inputs #
        # --------------- #
        df_inputs = utils.get_inputs_csv(
            app=app,
            working_path=working_path,
            study=key,
        )
        if df_inputs is not None:
            for dataset in df_inputs["ID"]:

                # execute
                df_inputs.loc[df_inputs["ID"] == dataset, "EXECUTE"] = int(value["Variable"][dataset]["execute"].value)

                # Variable params
                for k, v in value["Variable"][dataset]["params"].items():
                    if v.value is not None:
                        if (app.workflow.params_type[k][1] == "float"):
                            df_inputs.loc[df_inputs["ID"] == dataset, k] = float(v.value)
                        elif (app.workflow.params_type[k][1] == "int"):
                            df_inputs.loc[df_inputs["ID"] == dataset, k] = int(v.value)
                        elif (app.workflow.params_type[k][1] == "bool"):
                            df_inputs.loc[df_inputs["ID"] == dataset, k] = bool(v.value)
                        elif (app.workflow.params_type[k][1] == "str"):
                            df_inputs.loc[df_inputs["ID"] == dataset, k] = str(v.value)
                    else:
                        df_inputs.loc[df_inputs["ID"] == dataset, k] = v.value
                
                # Variable paths
                list_variable_paths = []
                if func is not None:
                    list_variable_paths = func(
                        working_path=working_path / f"{key}/0_inputs/0_datasets/{dataset}",
                        dict_widget_paths=value["Variable"][dataset]["paths"],
                    )

                for k, v in value["Variable"][dataset]["paths"].items():
                    if k not in list_variable_paths:
                        if v.value.strip() != "":
                            dict_inputs[k][dataset] = v.value
                        else:
                            dict_inputs[k][dataset] = None

            utils.update_inputs_csv(
                df_inputs=df_inputs,
                working_path=working_path,
                study=key,
            )

        utils.update_json_file(
            dict=dict_inputs,
            working_path=working_path,
            study=key,
            file_prefix="inputs",
        )


def analysis(
    dict_analysis_wgt: dict,
    working_path: Path,
) -> None:
    
    for study, analysis in dict_analysis_wgt.items():

        # ----------------- #
        # Analysis settings #
        # ----------------- #
        dict_analysis: dict = utils.get_json_file(
            working_path=working_path,
            study=study,
            file_prefix="analysis",
        )
        for proc, value in analysis.items():
            for dataset, settings in value.items():
                for k, v in settings.items():
                    dict_analysis[proc][dataset][k] = v.value
        
        utils.update_json_file(
            dict=dict_analysis,
            working_path=working_path,
            study=study,
            file_prefix="analysis",
        )