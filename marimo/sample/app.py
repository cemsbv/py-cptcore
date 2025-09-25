import marimo

__generated_with = "0.14.17"
app = marimo.App(width="full")


@app.cell
def _():
    import sys
    import os

    import marimo as mo
    import micropip
    return micropip, mo, os, sys


@app.cell
async def _(micropip, sys):
    if sys.platform == "emscripten":
        # running in Pyodide or other Emscripten based build
        await micropip.install(
            ["pyodide-http", "py-cptcore", "ssl", "cems-nuclei[client]"]
        )

        # Patch requests
        import pyodide_http

        pyodide_http.patch_all()

    from nuclei.client import NucleiClient

    import pycptcore
    return NucleiClient, pycptcore


@app.cell
def _(mo):
    jwt = mo.ui.text(placeholder="", label="NUCLEI JWT", kind="password")
    jwt
    return (jwt,)


@app.cell
def _(NucleiClient, jwt, os):
    if jwt.value != "":
        os.environ["NUCLEI_TOKEN"] = jwt.value

    if "NUCLEI_TOKEN" in os.environ:
        client = NucleiClient()
    else:
        raise ValueError("No JWT token provided")
    return (client,)


@app.cell
def _(mo):
    gef_file = mo.ui.file(filetypes=[".gef", ".GEF"])
    gef_file
    return (gef_file,)


@app.cell
def _(client, gef_file):
    response_parse = client.session.post(
        url="https://crux-nuclei.com/api/cptcore/v1/parse/cpt",
        json={
            "engine": "gef",
            "content": gef_file.value[0].contents.decode("utf-8", errors="ignore"),
        },
    )
    response_parse
    return (response_parse,)


@app.cell
def _(client, response_parse):
    data = response_parse.json()
    data["data"]["correctedPenetrationLength"] = data["data"]["penetrationLength"]
    if "depth" in data["data"].keys():
        data["data"]["correctedPenetrationLength"] = data["data"]["depth"]


    response_classify = client.session.post(
        url="https://crux-nuclei.com/api/cptcore/v1/classify/nen",
        json=data,
    )
    response_classify
    return (response_classify,)


@app.cell
def _(pycptcore, response_classify, response_parse):
    # create object
    result = pycptcore.SoilProperties.from_api_response(
        response_parse.json(), response_classify.json()
    )

    result.layer_table.dataframe
    return


if __name__ == "__main__":
    app.run()
