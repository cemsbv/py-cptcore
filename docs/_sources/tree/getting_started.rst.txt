.. ipython:: python
    :suppress:

    import os
    import json

    # get data from tests folder
    with open(
        os.path.join(
            os.environ.get("DOC_PATH"), "../tests/response/response_parse.json"
        ),
        "r",
    ) as file:
        response_parse = json.load(file)

    with open(
        os.path.join(
            os.environ.get("DOC_PATH"), "../tests/response/response_classify.json"
        ),
        "r",
    ) as file:
        response_classify = json.load(file)


Installing py-cptcore
=======================
To install :code:`pycptcore`, we strongly recommend using Python Package Index (PyPI).
You can install :code:`pycptcore` with:

.. code-block:: bash

    pip install pycptcore


How to import py-cptcore
==========================

Getting started with pycptcore is easy done by importing the :code:`pycptcore` library:

.. ipython:: python

    import pycptcore

or any equivalent :code:`import` statement.


How to initialize class
==========================

.. ipython:: python


    # create object
    result = pycptcore.SoilProperties.from_api_response(
        response_parse, response_classify
    )

    @savefig cpt_classify.png
    fig = result.plot()

    result.layer_table.dataframe
