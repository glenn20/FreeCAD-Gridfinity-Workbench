"""Makes grid layouts, calculates total width properties."""

from enum import StrEnum

import FreeCAD as fc  # noqa: N813

from . import const
from .base_properties import BaseProperties, ExpressionTuple, PropertyTuple


class GenerationLocationEnum(StrEnum):
    """String Enumeration for FreeCAD properties."""

    POSITIVE_FROM_ORIGIN = "Positive from Origin"
    CENTERED_AT_ORIGIN = "Centered at Origin"


class GridLayoutProperties(BaseProperties):
    """Grid Layout Properties."""

    GenerationLocation: GenerationLocationEnum
    xLocationOffset: fc.Units.Quantity
    yLocationOffset: fc.Units.Quantity
    xTotalWidth: fc.Units.Quantity
    yTotalWidth: fc.Units.Quantity
    xGridSize: fc.Units.Quantity
    yGridSize: fc.Units.Quantity
    Baseplate: bool

    # A class variable that defines the properties' values and types.
    _properties: PropertyTuple = (
        # User-facing properties
        (
            "GenerationLocation",
            [x.value for x in GenerationLocationEnum],
            "App::PropertyEnumeration",
            "Gridfinity",
            "Location of the bin. Change depending on how you want to customize",
        ),
        (
            "xGridSize",
            const.X_GRID_SIZE,
            "App::PropertyLength",
            "zzExpertOnly",
            "Size of each grid in x direction <br> <br> default = 42 mm",
        ),
        (
            "yGridSize",
            const.Y_GRID_SIZE,
            "App::PropertyLength",
            "zzExpertOnly",
            "Size of each grid in y direction <br> <br> default = 42 mm",
        ),
        # Computed (read-only) properties
        (
            "xTotalWidth",
            42,
            "App::PropertyLength",
            "ReferenceParameters",
            "total width of Gridfinity object in x direction",
            {"read_only": True},
        ),
        (
            "yTotalWidth",
            42,
            "App::PropertyLength",
            "ReferenceParameters",
            "total width of Gridfinity object in y direction",
            {"read_only": True},
        ),
        # Hidden properties
        (
            "Baseplate",
            False,
            "App::PropertyBool",
            "ShouldBeHidden",
            "Is the Gridfinity Object a baseplate",
            {"hidden": True},
        ),
        (
            "xLocationOffset",
            0,
            "App::PropertyLength",
            "ShouldBeHidden",
            "changing bin location in the x direction",
            {"hidden": True},
        ),
        (
            "yLocationOffset",
            0,
            "App::PropertyLength",
            "ShouldBeHidden",
            "changing bin location in the y direction",
            {"hidden": True},
        ),
    )


class GridRectangleLayoutProperties(GridLayoutProperties):
    """Grid Rectangle Layout Properties."""

    xGridUnits: float
    yGridUnits: float

    # A class variable that defines the properties' values and types.
    _properties: PropertyTuple = (
        # User-facing properties
        (
            "xGridUnits",
            const.X_GRID_UNITS,
            "App::PropertyFloat",
            "Gridfinity",
            "Number of grid units in the x direction <br> <br> default = 2",
        ),
        (
            "yGridUnits",
            const.Y_GRID_UNITS,
            "App::PropertyFloat",
            "Gridfinity",
            "Number of grid units in the y direction <br> <br> default = 2",
        ),
    )
    _expressions: ExpressionTuple = (
        (
            "xTotalWidth",
            "xGridUnits * xGridSize - (Baseplate == 1 ? 0 mm : 2 * Clearance)",
        ),
        (
            "yTotalWidth",
            "yGridUnits * yGridSize - (Baseplate == 1 ? 0 mm : 2 * Clearance)",
        ),
    )


def rectangle_layout_properties(
    obj: GridRectangleLayoutProperties, *, baseplate_default: bool
) -> None:
    """Create Rectangle Layout.

    Args:
        obj (GridRectangleLayoutProperties): Grid layout object
        baseplate_default (bool): is Gridfinity Object baseplate

    """
    obj.Baseplate = baseplate_default


def make_rectangle_layout(obj: GridRectangleLayoutProperties) -> list[list[bool]]:
    """Generate Rectangle layout and calculate relevant parameters."""
    if obj.GenerationLocation == GenerationLocationEnum.CENTERED_AT_ORIGIN:
        if obj.Baseplate:
            obj.xLocationOffset = obj.xTotalWidth / 2
            obj.yLocationOffset = obj.yTotalWidth / 2
        else:
            obj.xLocationOffset = obj.xTotalWidth / 2 + obj.Clearance
            obj.yLocationOffset = obj.yTotalWidth / 2 + obj.Clearance
    else:
        obj.xLocationOffset.Value = 0
        obj.yLocationOffset.Value = 0

    return [[True] * int(obj.yGridUnits + 1e-6) for x in range(int(obj.xGridUnits + 1e-6))]


def custom_shape_layout_properties(obj: GridLayoutProperties, *, baseplate_default: bool) -> None:
    """Add relevant properties for a custom shape gridfinity object.

    Args:
        obj (GridLayoutObject): Grid layout object
        baseplate_default (Bool): is Gridfinity Object baseplate

    """
    obj.Baseplate = baseplate_default
    obj.setEditorMode("GenerationLocation", 2)


def make_custom_shape_layout(obj: GridLayoutProperties, layout: list[list[bool]]) -> None:
    """Calculate values for custom shape.

    Args:
        obj (GridLayoutObject): Grid layout object
        layout (list[list[bool]]): Layout of the gridfinity grid.

    """
    x_grid_pos = []
    y_max_pos = []
    y_min_pos = []

    for i, col in enumerate(layout):
        y_grid_pos = [i for i, y in enumerate(col) if y]
        if y_grid_pos:
            y_min_pos.append(min(y_grid_pos))
            y_max_pos.append(max(y_grid_pos))
            x_grid_pos.append(i)

    x_min_grid = min(x_grid_pos) + 1
    x_max_grid = max(x_grid_pos) + 1
    y_min_grid = min(y_min_pos) + 1
    y_max_grid = max(y_max_pos) + 1

    if obj.Baseplate:
        obj.xTotalWidth = (x_max_grid + 1 - x_min_grid) * obj.xGridSize
        obj.yTotalWidth = (y_max_grid + 1 - y_min_grid) * obj.yGridSize
    else:
        obj.xTotalWidth = (x_max_grid + 1 - x_min_grid) * obj.xGridSize - obj.Clearance * 2
        obj.yTotalWidth = (y_max_grid + 1 - y_min_grid) * obj.yGridSize - obj.Clearance * 2
