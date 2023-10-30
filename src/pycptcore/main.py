from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal, Sequence, Tuple, Union

import matplotlib.ticker as plticker
import pandas as pd
import requests
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

Number = Union[float, int]
TickLoc = plticker.MultipleLocator(base=0.5)


@dataclass(frozen=True)
class Location:
    """DataClass that holds the standardized location information"""

    srs_name: str
    long: float
    lat: float

    @property
    def transform(self) -> dict:
        """transform EPSG 4326 to EPSG 28992 with epsg.io"""
        response = requests.get(
            f"https://epsg.io/trans?s_srs=4326&t_srs=28992&x={self.long}&y={self.lat}&format=json"
        )
        if response.ok:
            return json.loads(response.text)
        raise RuntimeError(response.content)


@dataclass(frozen=True)
class LayerTable:
    """
    Object that contains the Soil-layer data-traces.

    Attributes:
    ------------
    geotechnicalSoilName: Sequence[str]
        geotechnical Soil Name related to the ISO
    lowerBoundary: Sequence[float]
        lower boundary of the layer [m]
    upperBoundary: Sequence[float]
        upper boundary of the layer [m]
    color: Sequence[str]
        hex color code
    mainComponent: Sequence[Literal["rocks", "gravel", "sand", "silt", "clay", "peat"]]
        main soil component
    cohesion: Sequence[float]
        cohesion of the layer [kPa]
    gamma_sat: Sequence[float]
        Saturated unit weight [kN/m^3]
    gamma_unsat: Sequence[float]
        unsaturated unit weight [kN/m^3]
    phi: Sequence[float]
        phi [degrees]
    undrainedShearStrength: Sequence[float]
        undrained shear strength [kPa]
    """

    geotechnicalSoilName: Sequence[str]
    lowerBoundary: Sequence[float]
    upperBoundary: Sequence[float]
    color: Sequence[str]
    mainComponent: Sequence[Literal["rocks", "gravel", "sand", "silt", "clay", "peat"]]
    cohesion: Sequence[float]
    gamma_sat: Sequence[float]
    gamma_unsat: Sequence[float]
    phi: Sequence[float]
    undrainedShearStrength: Sequence[float]

    def __post_init__(self) -> None:
        raw_lengths = [len(values) for values in self.__dict__.values()]
        if len(list(set(raw_lengths))) > 1:
            raise ValueError("All values in this dataclass must have the same length.")

    @classmethod
    def from_api_response(cls, response_dict: dict) -> "LayerTable":
        """
        Stores the response of the CPTCore endpoint

        Parameters
        ----------
        response_dict:
           The resulting response of a call to `classify/*`
        """
        return cls(
            geotechnicalSoilName=response_dict.get("geotechnicalSoilName"),  # type: ignore
            lowerBoundary=response_dict.get("lowerBoundary"),  # type: ignore
            upperBoundary=response_dict.get("upperBoundary"),  # type: ignore
            color=response_dict.get("color"),  # type: ignore
            mainComponent=response_dict.get("mainComponent"),  # type: ignore
            cohesion=response_dict.get("cohesion"),  # type: ignore
            gamma_sat=response_dict.get("gamma_sat"),  # type: ignore
            gamma_unsat=response_dict.get("gamma_unsat"),  # type: ignore
            phi=response_dict.get("phi"),  # type: ignore
            undrainedShearStrength=response_dict.get("undrainedShearStrength"),  # type: ignore
        )

    @property
    def dataframe(self) -> pd.DataFrame:
        """The pandas.DataFrame representation"""
        return pd.DataFrame(self.__dict__).dropna(axis="rows", how="any")  # type: ignore

    def plot(
        self, axes: plt.Axes | None = None, offset: float = 0, **kwargs: Any
    ) -> None:
        """
        Plot the soil-layer in a subplot

        Parameters
        ----------
        axes:
            `plt.Axes` object where the data can be plotted on.
        offset:
            offset sue to plot upper and lower boundary of the soil layer
        **kwargs:
            All additional keyword arguments are passed to the `pyplot.subplots()` call.
        """
        if axes is None:
            _, axes = plt.subplots(**kwargs)

        for _, row in self.dataframe.iterrows():
            lower_boundary = offset - row["lowerBoundary"]
            upper_boundary = offset - row["upperBoundary"]

            axes.fill_between(
                [0, 1],
                lower_boundary,
                upper_boundary,
                color=row["color"],
            )

            # add annotate
            y = (lower_boundary - upper_boundary) / 2 + upper_boundary
            axes.annotate(
                text=row["geotechnicalSoilName"],
                xy=(0.25, y),
                fontsize=5,
            )
        axes.invert_yaxis()
        axes.set_xticklabels([])


@dataclass(frozen=True)
class CPTTable:
    """
    Object that contains the CPT-related data-traces.

    Attributes:
    ------------
    penetrationLength: Sequence[float]
        CPT penetrationLength [m]
    depthOffset: Sequence[float]
        CPT depth [m w.r.t. Reference]
    coneResistance: Sequence[float]
        cone resistance [Mpa]
    localFriction: Sequence[float]
        local friction [Mpa]
    frictionRatio: Sequence[float]
        friction ratio [-]
    """

    penetrationLength: Sequence[float]
    depthOffset: Sequence[float]
    coneResistance: Sequence[float]
    localFriction: Sequence[float]
    frictionRatio: Sequence[float]

    def __post_init__(self) -> None:
        raw_lengths = [len(values) for values in self.__dict__.values()]
        if len(list(set(raw_lengths))) > 1:
            raise ValueError("All values in this dataclass must have the same length.")

    @classmethod
    def from_api_response(cls, response_dict: dict) -> "CPTTable":
        """
        Stores the response of the CPTCore endpoint

        Parameters
        ----------
        response_dict:
           The resulting response of a call to `cpt/parse`
        """
        return cls(
            penetrationLength=response_dict.get(
                "depth", response_dict.get("penetrationLength")
            ),
            depthOffset=response_dict.get("depthOffset"),  # type: ignore
            coneResistance=response_dict.get("coneResistance"),  # type: ignore
            localFriction=response_dict.get("localFriction"),  # type: ignore
            frictionRatio=response_dict.get(
                "frictionRatio", response_dict.get("frictionRatioComputed")
            ),
        )

    @property
    def dataframe(self) -> pd.DataFrame:
        """The pandas.DataFrame representation"""
        return pd.DataFrame(self.__dict__).dropna(axis="rows", how="any")  # type: ignore

    def plot_cone_resistance(
        self,
        axes: Axes | None = None,
        offset: float = 0,
        **kwargs: Any,
    ) -> None:
        """
        Plots the cone resistance.

        Parameters
        ----------
        axes:
            Optional Axes to plot on.
        offset:
            offset used to plot depth
        **kwargs:
            All additional keyword arguments are passed to the `pyplot.subplots()` call.
        """

        if axes is None:
            _, axes = plt.subplots(**kwargs)

        axes.xaxis.set_ticks_position("top")
        axes.xaxis.set_label_position("top")
        axes.spines["top"].set_position(("axes", 1))
        axes.set_xlim(0, 40)
        axes.set_xlabel("$q_c$ [MPa]")
        axes.xaxis.label.set_color("#2d2e87")
        axes.invert_yaxis()

        axes.plot(
            self.coneResistance,
            [offset - value for value in self.penetrationLength],
            color="#2d2e87",
            label="coneResistance",
        )

    def plot_local_friction(
        self,
        axes: Axes | None = None,
        offset: float = 0,
        **kwargs: Any,
    ) -> None:
        """
        Plots the local-friction data.

        Parameters
        ----------
        axes:
            Optional Axes to plot on.
        offset:
            offset used to plot depth
        **kwargs:
            All additional keyword arguments are passed to the `pyplot.subplots()` call.
        """

        if axes is None:
            _, axes = plt.subplots(**kwargs)

        axes.xaxis.set_ticks_position("top")
        axes.xaxis.set_label_position("top")
        axes.spines["top"].set_position(("axes", 1.05))
        axes.set_xlabel("$f_s$ [MPa]")
        axes.set_xlim(0, 0.8)
        axes.xaxis.label.set_color("#e04913")
        axes.invert_yaxis()

        # add friction number subplot
        axes.plot(
            self.localFriction,
            [offset - value for value in self.penetrationLength],
            color="#e04913",
            label="localFriction",
        )

    def plot_friction_ratio(
        self,
        axes: Axes | None = None,
        offset: float = 0,
        **kwargs: Any,
    ) -> None:
        """
        Plots the friction-ratio data.

        Parameters
        ----------
        axes:
            Optional Axes to plot on.
        offset:
            offset used to plot depth
        **kwargs:
            All additional keyword arguments are passed to the `pyplot.subplots()` call.
        """

        if axes is None:
            _, axes = plt.subplots(**kwargs)

        axes.xaxis.set_ticks_position("top")
        axes.xaxis.set_label_position("top")
        axes.spines["top"].set_position(("axes", 1.1))
        axes.set_xlabel("$R_f$ [%]")
        axes.set_xlim(0, 16)
        axes.invert_xaxis()
        axes.xaxis.label.set_color("tab:gray")
        axes.invert_yaxis()

        # add friction number subplot
        axes.plot(
            self.frictionRatio,
            [offset - value for value in self.penetrationLength],
            color="tab:gray",
            label="frictionRatio",
        )


@dataclass(frozen=True)
class SoilProperties:
    """
    A class for soil properties.

    Attributes:
    ------------
    cpt_table: CPTTable
        CPT object
    layer_table: LayerTable
        layer table object
    location: Location
        spatial object
    verticalPositionReferencePoint: str
        vertical position reference point
    verticalPositionOffset: float
        vertical position offset [m w.r.t. reference]
    predrilledDepth: float
        predrilled depth [m]
    label: str
        CPT name
    groundwaterLevel: float
        groundwater level [m]
    """

    cpt_table: CPTTable
    layer_table: LayerTable
    location: Location
    verticalPositionReferencePoint: str
    verticalPositionOffset: float
    predrilledDepth: float | None
    label: str
    groundwaterLevel: float | None

    @classmethod
    def from_api_response(
        cls, response_parse: dict, response_classify: dict
    ) -> "SoilProperties":
        """
        Stores the response of the CPTCore endpoint

        Parameters
        ----------
        response_parse:
           The resulting response of a call to `cpt/parse`
        response_classify:
           The resulting response of a call to `classify/*`
        """
        location = response_parse.get("location", {})

        return cls(
            cpt_table=CPTTable.from_api_response(response_parse.get("data", {})),
            layer_table=LayerTable.from_api_response(response_classify),
            location=Location(
                lat=location.get("lat"),
                long=location.get("long"),
                srs_name=location.get("srs"),
            ),
            verticalPositionReferencePoint=response_parse.get(
                "verticalPositionReferencePoint", "Unknown"
            ),
            verticalPositionOffset=response_parse.get("verticalPositionOffset", 0),
            predrilledDepth=response_parse.get("predrilledDepth"),
            label=response_parse.get("label", "Unknown"),
            groundwaterLevel=response_parse.get("groundwaterLevel"),
        )

    def plot(
        self,
        figsize: Tuple[float, float] = (10.0, 12.0),
        width_ratios: Tuple[float, float] = (1.0, 0.1),
        **kwargs: Any,
    ) -> Figure:
        """
        Plots the CPT and soil table data.

        Parameters
        ----------
        figsize:
            Size of the activate figure, as the `plt.figure()` argument.
        width_ratios:
            Tuple of width-ratios of the subplots, as the `plt.GridSpec` argument.
        **kwargs:
            All additional keyword arguments are passed to the `pyplot.subplots()` call.

        Returns
        -------
        fig:
            The matplotlib Figure
        """

        kwargs_subplot = {
            "gridspec_kw": {"width_ratios": width_ratios},
            "sharey": "row",
            "figsize": figsize,
            "tight_layout": True,
        }

        kwargs_subplot.update(kwargs)

        fig, _ = plt.subplots(
            1,
            2,
            **kwargs_subplot,
        )

        ax_qc, ax_layers = fig.axes

        ax_rf = ax_qc.twiny()
        ax_fs = ax_qc.twiny()

        # create grid
        major_ticks = range(0, 41, 5)
        minor_ticks = range(0, 41, 1)
        ax_qc.set_xticks(major_ticks)
        ax_qc.set_xticks(minor_ticks, minor=True)
        ax_qc.grid(which="both")
        ax_qc.grid(which="minor", alpha=0.2)
        ax_qc.grid(which="major", alpha=0.5)
        ax_qc.yaxis.set_major_locator(TickLoc)

        # Plot horizontal lines
        if self.groundwaterLevel:
            ax_qc.axhline(
                y=self.verticalPositionOffset - self.groundwaterLevel,
                color="tab:blue",
                linestyle="--",
                label="Groundwater level",
            )

        if self.predrilledDepth:
            ax_qc.axhline(
                y=self.verticalPositionOffset - self.predrilledDepth,
                color="tab:brown",
                linestyle="--",
                label="Surface level",
            )

        self.cpt_table.plot_cone_resistance(ax_qc, offset=self.verticalPositionOffset)
        self.cpt_table.plot_local_friction(ax_fs, offset=self.verticalPositionOffset)
        self.cpt_table.plot_friction_ratio(ax_rf, offset=self.verticalPositionOffset)
        self.layer_table.plot(axes=ax_layers, offset=self.verticalPositionOffset)

        return fig
