from enum import Enum
from pathlib import Path
import re

import yaml

from src.core.exceptions import FieldValidationError

from typing import Union, Optional, Dict, Any


class FieldType(Enum):
    TEXT = 'text'
    NUMBER = 'number'
    MEASURE = 'measure'
    COLOR = 'color'
    PATH = 'path'


class Measure:
    class MeasureUnit(str, Enum):
        MILLIS = 'mm'
        PERCENT = '%'

    def __init__(self, value: float, unit: MeasureUnit):
        self._magnitude = value
        self._unit = unit

    @classmethod
    def parse(cls, input_str):
        for mt in cls.MeasureUnit:
            suffix_size = len(mt)
            if mt in input_str[-suffix_size:]:
                number = float(input_str[0:-suffix_size])
                units = cls.MeasureUnit(mt)

                return cls(number, units)
        else:
            raise TypeError(f'Unrecognized measure type for input "{input_str}"')

    def __str__(self):
        return str(self._magnitude) + str(self._unit.value)

    def __add__(self, other):
        if isinstance(other, Measure):
            if self._unit != other._unit:
                raise NotImplementedError('Cannot operate with different units yet')
            else:
                return Measure(self._magnitude + other._magnitude, self._unit)
        else:
            return Measure(self._magnitude + other, self._unit)

    def __sub__(self, other):
        if isinstance(other, Measure):
            if self._unit != other._unit:
                raise NotImplementedError('Cannot operate with different units yet')
            else:
                return Measure(self._magnitude - other._magnitude, self._unit)
        else:
            return Measure(self._magnitude - other, self._unit)

    def __mul__(self, other):
        if isinstance(other, Measure):
            if self._unit != other._unit:
                raise NotImplementedError('Cannot operate with different units yet')
            else:
                return Measure(self._magnitude * other._magnitude, self._unit)
        else:
            return Measure(self._magnitude * other, self._unit)


class Reference:
    def __init__(self, target):
        self._target = target
        self._type = None

    def get_target(self):
        return self._target

    @classmethod
    def from_yaml_node(cls, loader: yaml.Loader, node):
        return cls(loader.construct_scalar(node))


class Field:

    def __init__(self, value_type: Union[str, FieldType], editable=True, value=None):

        self._type = FieldType(value_type)
        self._editable = editable
        self._target = None

        self._value = None
        if value is not None:
            self._force_set_value(value)

    def is_editable(self):
        return self._editable

    def is_reference(self):
        return self._target is not None

    def get_target(self):
        return self._target

    def get_type(self):
        return self._type

    def set_value(self, new_value: str):
        if not self.is_editable():
            raise FieldValidationError(f'Trying to edit a non editable field. '
                                       f'Current value: "{self._value}", new value: "{new_value}"')
        self._force_set_value(new_value)

    def get_value(self, record: "Record" = None):
        from src.core.data.manifest import Record
        if record is None:
            record = Record()
        if self.is_reference():
            record.validate_reference(self.get_target(), self.get_type())
            return record.get_field(self._target).get_value()
        else:
            return self._value

    def _force_set_value(self, new_value: Union[str, Reference]):
        if isinstance(new_value, Reference):
            self._target = new_value.get_target()
            self._value = None
        else:
            match self._type:
                case FieldType.TEXT:
                    self._value = str(new_value)
                case FieldType.NUMBER:
                    self._value = float(new_value)
                case FieldType.MEASURE:
                    self._value = Measure.parse(new_value)
                case FieldType.COLOR:
                    # Check that input values is a valid hexadecimal color
                    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', new_value)
                    if not match:
                        raise ValueError(f'Value "{new_value}" is not a valid hexadecimal color string')
                    self._value = str(new_value)
                case FieldType.PATH:
                    self._value = Path(new_value)

            self._target = None

    def __str__(self):
        return f'[type: {self._type}; value: {self._value}]'
