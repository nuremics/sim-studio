import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")

with app.setup(hide_code=True):
    import os
    import subprocess
    from pathlib import Path

    import marimo as mo
    from nuremics_labs.system import main

    import nuremics_studio.core.update as upt
    import nuremics_studio.core.utils as utils
    import nuremics_studio.core.widgets as wgt

    app_id = os.getenv("NUREMICS_APP").split(".")
    app_category = app_id[0]
    app_name = app_id[1]

    app_features = utils.get_app_features(
        app_category=app_category,
        app_name=app_name,
    )
    app_logo = app_features["logo"]
    app_color = "#" + app_features["color"]
    app_deps = app_features["dependencies"]
    app_visual = app_features["visual"]
    app_link = app_features["app_link"]
    use_case_link = app_features["use_case_link"]
    use_case_title = app_features["use_case_title"]
    use_case_description = app_features["use_case_description"]
    app_config = app_features["config"]


@app.cell(hide_code=True)
def _():
    app_banner_wgt = wgt.app_banner(
        app_name=app_name,
        app_logo=app_logo,
        app_color=app_color,
        app_link=app_link,
    )
    app_banner_wgt
    return


@app.cell(hide_code=True)
def _():
    use_case_wgt = wgt.use_case(
        color=app_color,
        visual=app_visual,
        use_case_link=use_case_link,
        use_case_title=use_case_title,
        use_case_description=use_case_description,
        dependencies=app_deps,
    )
    use_case_wgt
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 🧪 Configuration
    -----------------------------
    """)
    return


@app.cell(hide_code=True)
def _():
    app = main(
        app_id=app_id,
        stage=None,
    )
    default_params = app.default_params

    dict_settings = utils.get_settings()

    if dict_settings["apps"][app_category][app_name]["working_dir"] is not None:
        working_dir = dict_settings["apps"][app_category][app_name]["working_dir"]
    else:
        if dict_settings["default_working_dir"] is not None:
            working_dir = dict_settings["default_working_dir"]
        else:
            working_dir = ""
    return app, default_params, dict_settings, working_dir


@app.cell(hide_code=True)
def _(working_dir):
    working_dir_wgt = wgt.working_dir(
        working_dir=working_dir,
    )
    working_dir_wgt
    return (working_dir_wgt,)


@app.cell(hide_code=True)
def _(working_dir_wgt):
    is_valid_working_dir = working_dir_wgt.value != ""
    return (is_valid_working_dir,)


@app.cell(hide_code=True)
def _(is_valid_working_dir):
    mo.stop(not is_valid_working_dir)

    get_state_sc, set_state_sc = mo.state(0)

    sc_config_wgt, dict_sc_config_wgt = wgt.splinecloud_config(
        app_config=app_config,
        set_state=set_state_sc,
    )
    sc_config_wgt
    return dict_sc_config_wgt, get_state_sc


@app.cell(hide_code=True)
def _(dict_sc_config_wgt, get_state_sc, is_valid_working_dir, working_dir_wgt):
    mo.stop(not is_valid_working_dir)

    _ = get_state_sc()

    if app_config is not None:
        if dict_sc_config_wgt["config_button"].value:
            subprocess.run(
                app_config,
                cwd=working_dir_wgt.value,
                shell=True,
                check=True,
            )
    return


@app.cell(hide_code=True)
def _(is_valid_working_dir):
    mo.stop(not is_valid_working_dir)

    mo.md(
        r"""
        ### 📚 Studies
        -----------------------------
        """
    )
    return


@app.cell(hide_code=True)
def _(dict_settings, get_state_sc, is_valid_working_dir, working_dir_wgt):
    mo.stop(not is_valid_working_dir)

    _ = get_state_sc()

    dict_settings["apps"][app_category][app_name]["working_dir"] = working_dir_wgt.value

    utils.update_settings(
        dict_settings=dict_settings,
    )

    working_path = Path(working_dir_wgt.value) / app_name

    utils.load_local_server(
        working_path=working_path,
    )

    try:
        main(
            app_id=app_id,
            stage="config",
        )
    except SystemExit:
        pass
    return (working_path,)


@app.cell(hide_code=True)
def _(working_path):
    dict_studies_init = utils.get_studies(
        working_path=working_path,
    )

    studies_wgt = wgt.studies(
        list_studies=dict_studies_init["studies"],
    )
    studies_wgt
    return (studies_wgt,)


@app.cell(hide_code=True)
def _(studies_wgt):
    list_studies = [
        s for s in studies_wgt.value["Studies"].tolist() if s != ""
    ]
    is_valid_list_studies = bool(list_studies)
    return is_valid_list_studies, list_studies


@app.cell(hide_code=True)
def _(is_valid_list_studies, list_studies, working_path):
    mo.stop(not is_valid_list_studies)

    utils.update_list_studies(
        working_path=working_path,
        list_studies=list_studies,
    )

    try:
        main(
            app_id=app_id,
            stage="config",
        )
    except SystemExit:
        pass

    dict_studies_to_config = utils.get_studies(
        working_path=working_path,
    )
    return (dict_studies_to_config,)


@app.cell(hide_code=True)
def _(dict_studies_to_config, is_valid_list_studies):
    mo.stop(not is_valid_list_studies)

    get_state_config, set_state_config = mo.state(0)

    config_wgt, dict_config_wgt = wgt.config(
        dict_studies=dict_studies_to_config,
        set_state=set_state_config,
    )
    config_wgt
    return dict_config_wgt, get_state_config


@app.cell(hide_code=True)
def _(
    dict_config_wgt,
    dict_studies_to_config,
    get_state_config,
    is_valid_list_studies,
    working_path,
):
    mo.stop(not is_valid_list_studies)

    _ = get_state_config()

    dict_studies_configured = upt.dict_studies(
        dict_studies=dict_studies_to_config,
        dict_config_wgt=dict_config_wgt,
    )

    utils.update_studies(
        working_path=working_path,
        dict_studies=dict_studies_configured,
    )

    try:
        app_configured = main(
            app_id=app_id,
            stage="config",
        )
    except SystemExit:
        pass
    return (app_configured,)


@app.cell(hide_code=True)
def _(is_valid_list_studies):
    mo.stop(not is_valid_list_studies)

    mo.vstack([
        mo.md("    "),
        mo.md("    "),
    ])
    return


@app.cell(hide_code=True)
def _(is_valid_list_studies):
    mo.stop(not is_valid_list_studies)

    mo.md(
        r"""
        ### ⚙️ Settings
        -----------------------------
        """
    )
    return


@app.cell(hide_code=True)
def _(
    app_configured,
    get_state_config,
    is_valid_list_studies,
    list_studies,
    working_path,
):
    mo.stop(not is_valid_list_studies)

    _ = get_state_config()

    get_state_datasets, set_state_datasets = mo.state(0)

    datasets_wgt, dict_datasets_wgt = wgt.datasets(
        app=app_configured,
        working_path=working_path,
        list_studies=list_studies,
        set_state=set_state_datasets,
    )
    datasets_wgt
    return dict_datasets_wgt, get_state_datasets


@app.cell(hide_code=True)
def _(
    app,
    dict_datasets_wgt,
    get_state_datasets,
    is_valid_list_studies,
    working_path,
):
    mo.stop(not is_valid_list_studies)

    _ = get_state_datasets()

    upt.datasets(
        app=app,
        dict_datasets_wgt=dict_datasets_wgt,
        working_path=working_path,
    )
    return


@app.cell(hide_code=True)
def _(get_state_datasets, is_valid_list_studies):
    mo.stop(not is_valid_list_studies)

    _ = get_state_datasets()

    try:
        main(
            app_id=app_id,
            stage="settings",
        )
    except SystemExit:
        pass
    return


@app.cell(hide_code=True)
def _(
    app_configured,
    default_params,
    get_state_config,
    get_state_datasets,
    is_valid_list_studies,
    list_studies,
    working_path,
):
    mo.stop(not is_valid_list_studies)

    _ = get_state_config()
    _ = get_state_datasets()

    get_state_settings, set_state_settings = mo.state(0)

    settings_wgt, dict_settings_wgt = wgt.settings(
        app=app_configured,
        default_params=default_params,
        working_path=working_path,
        list_studies=list_studies,
        set_state=set_state_settings,
    )
    settings_wgt
    return dict_settings_wgt, get_state_settings


@app.cell(hide_code=True)
def _(
    app,
    dict_settings_wgt,
    get_state_settings,
    is_valid_list_studies,
    working_path,
):
    mo.stop(not is_valid_list_studies)

    _ = get_state_settings()

    upt.studies_settings(
        app=app,
        dict_settings_wgt=dict_settings_wgt,
        working_path=working_path,
    )
    return


@app.cell(hide_code=True)
def _(get_state_datasets, get_state_settings, is_valid_list_studies):
    mo.stop(not is_valid_list_studies)

    _ = get_state_settings()
    _ = get_state_datasets()

    kind = None

    try:
        main(
            app_id=app_id,
            stage="settings",
        )
        kind = "success"
    except SystemExit:
        kind = "danger"
    return (kind,)


@app.cell(hide_code=True)
def _(is_valid_list_studies, kind):
    mo.stop(not is_valid_list_studies)

    run_button = mo.ui.run_button(
        kind=kind,
        label="Run App",
        full_width=False,
    )
    mo.vstack(
        [
            mo.vstack([mo.md("    ")]),
            mo.vstack([mo.md("    ")]),
            mo.vstack([mo.md("    ")]),
            mo.vstack([run_button]),
        ], align="center",
    )
    return (run_button,)


@app.cell(hide_code=True)
def _(run_button):
    mo.stop(not run_button.value)

    success = None

    try:
        main(
            app_id=app_id,
            stage="run",
        )
        message = mo.vstack(
            [mo.md("<span style='color: green; font-size: 3.5em;'>✔</span>")],
            align="center",
        )
        success = True
    except SystemExit:
        message = mo.vstack(
            [mo.md("<span style='color: red; font-size: 3.5em;'>✘</span>")],
            align="center",
        )
        success = False
    return message, success


@app.cell
def _(message):
    message
    return


@app.cell(hide_code=True)
def _(success):
    mo.stop(not success)

    mo.md(
        r"""
        ## 📊 Results
        -----------------------------
        """
    )
    return


@app.cell(hide_code=True)
def _(success, working_path):
    mo.stop(not success)

    mo.vstack([mo.ui.file_browser(initial_path=working_path)])
    return


@app.cell(hide_code=True)
def _(success):
    mo.stop(not success)

    mo.md(
        r"""
        ### ⚙️ Settings
        -----------------------------
        """
    )
    return


@app.cell(hide_code=True)
def _(list_studies, success, working_path):
    mo.stop(not success)

    get_state_analysis, set_state_analysis = mo.state(0)

    analysis_wgt, dict_analysis_wgt = wgt.analysis(
        working_path=working_path,
        list_studies=list_studies,
        set_state=set_state_analysis,
    )
    analysis_wgt
    return dict_analysis_wgt, get_state_analysis


@app.cell(hide_code=True)
def _(dict_analysis_wgt, get_state_analysis, success, working_path):
    mo.stop(not success)

    _ = get_state_analysis()

    upt.analysis(
        dict_analysis_wgt=dict_analysis_wgt,
        working_path=working_path,
    )
    return


@app.cell(hide_code=True)
def _(success):
    mo.stop(not success)

    mo.vstack([
        mo.md("    "),
        mo.md("    "),
        mo.md("    "),
    ])
    return


@app.cell(hide_code=True)
def _(success):
    mo.stop(not success)

    mo.md(
        r"""
        ### 👁️ Visualization
        -----------------------------
        """
    )
    return


@app.cell(hide_code=True)
def _(app, get_state_analysis, list_studies, success, working_path):
    mo.stop(not success)

    _ = get_state_analysis()

    results_wgt = wgt.results(
        app=app,
        working_path=working_path,
        list_studies=list_studies,
    )
    results_wgt
    return


if __name__ == "__main__":
    app.run()
