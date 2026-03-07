"""Base Properties for Gridfinity Objects."""

from __future__ import annotations

from typing import Any

import FreeCAD as fc  # noqa: N813

PropertyTuple = tuple[
    tuple[str, Any, str, str, str, dict[str, Any]] | tuple[str, Any, str, str, str],
    ...,
]
ExpressionTuple = tuple[
    tuple[str, str],
    ...,
]


class BaseProperties(fc.DocumentObject):
    """Base Object for Gridfinity Objects."""

    _properties: PropertyTuple
    _expressions: ExpressionTuple

    @classmethod
    def check_properties(cls, obj: fc.DocumentObject) -> None:
        """Check that all properties are initialized and of expected type."""
        classes = reversed([cls for cls in cls.__mro__ if issubclass(cls, BaseProperties)])
        expressionengine = dict(obj.ExpressionEngine)
        for class_ in classes:
            if hasattr(class_, "_properties"):
                for props in class_._properties:  # noqa: SLF001
                    name, _expected_value, expected_type, _group, _description, *_extra = props
                    if (prop_id := obj.getTypeIdOfProperty(name)) != expected_type:
                        raise TypeError(
                            f"Property {name} has incorrect type {prop_id}, "
                            f"expected {expected_type}.",
                        )

            if hasattr(class_, "_expressions"):
                for name, _expression in class_._expressions:  # noqa: SLF001
                    if name not in expressionengine:
                        raise AttributeError(
                            f"Expression for {name} has not been set in {obj}.",
                        )
                    # if str(expressionengine[name]) != str(expression):
                    #     raise ValueError(
                    #         f"Expression for {name} is not set correctly in {obj}. "
                    #         f"Expected: '{expression}', got: '{expressionengine[name]}'",
                    #     )

    @classmethod
    def init_properties(cls, obj: fc.DocumentObject) -> None:
        """Initialise the properties and expressions on the DocumentObject."""
        classes = reversed([cls for cls in cls.__mro__ if issubclass(cls, BaseProperties)])
        for class_ in classes:
            if hasattr(class_, "_properties"):
                fc.Console.PrintLog(f"{class_.__name__}: {class_._properties}\n")  # noqa: SLF001
                for props in class_._properties:  # noqa: SLF001
                    name, value, prop_type, group, description, *extra = props
                    kwargs = extra[0] if extra else {}
                    try:
                        obj.addProperty(prop_type, name, group, description, **kwargs)
                    except NameError as e:
                        raise NameError(
                            f"Error adding property '{name}' of type '{prop_type}' "
                            f"to object '{obj.Name}': {e}",
                        ) from e
                    if value is not None:
                        setattr(obj, name, value)

            if hasattr(class_, "_expressions"):
                for name, expression in class_._expressions:  # noqa: SLF001
                    obj.setExpression(name, expression)
        cls.check_properties(obj)
