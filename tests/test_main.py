import matplotlib.pyplot as plt

from pycptcore import SoilProperties


def test_grouper_results(
    mock_response_parse: dict, mock_response_classify: dict
) -> None:
    """
    Test parsing and plotting in GrouperResults object
    """

    # test parsing of response to dataclass
    result = SoilProperties.from_api_response(
        mock_response_parse, mock_response_classify
    )

    # test plotting
    plot = result.plot()
    assert isinstance(plot, plt.Figure)

    plot.savefig("./fig.png")


def test_grouper_results_A(
    mock_response_parse: dict, mock_response_classify: dict
) -> None:
    """
    Test parsing and plotting in GrouperResults object
    """

    # test parsing of response to dataclass
    result = SoilProperties.from_api_response(mock_response_parse)

    result.set_layer_table_from_api_response(mock_response_classify)

    # test plotting
    plot = result.plot()
    assert isinstance(plot, plt.Figure)

    plot.savefig("./fig.png")
