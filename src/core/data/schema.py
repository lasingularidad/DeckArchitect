from collections import OrderedDict

from src.core.data.fields import Field, FieldType
from src.core.exceptions import SchemaValidationError

from typing import List


class DataSchema(OrderedDict):

    def __init__(self, field_names, field_types):
        if len(field_names) != len(field_types):
            raise ValueError(f'Number of field names ({len(field_names)}) '
                             f'is not equal to number of field types ({len(field_types)})')

        # Convert field type names to FieldType if needed
        field_types = [f_type if isinstance(f_type, FieldType) else FieldType(f_type)
                       for f_type in field_types]

        data = {f_names: f_types for f_names, f_types in zip(field_names, field_types)}
        super().__init__(data)

    def get_field_names(self):
        return self.keys()

    def populate_fields(self, values: List[str]):
        if len(self.keys()) != len(values):
            raise SchemaValidationError(f'Number of input fields ({len(values)}) '
                                        f'is not equal to number of expected fields ({len(self.keys())})')
        field_list = [Field(f_type, value=f_data, editable=False)
                      for (f_name, f_type), f_data in zip(self.items(), values, strict=True)]
        return field_list

    def validate_record(self, record: "Record", extra_field_error=True):
        # Record has all required fields
        missing_fields = set(self.get_field_names()).difference(record.get_field_names())
        if len(missing_fields) > 0:
            raise SchemaValidationError(f'Input record does not fulfills current data schema. '
                                        f'{len(missing_fields)} fields missing: {missing_fields}')

        # Record does not have extra fields
        if extra_field_error:
            extra_fields = set(record.get_field_names()).difference(self.get_field_names())
            if len(extra_fields) > 0:
                raise SchemaValidationError(f'Input record does not fulfills current data schema. '
                                            f'{len(extra_fields)} extra fields not present on schema: {extra_fields}')

        # Schema and record types are the same
        for f_name in self.get_field_names():
            if self[f_name] != record.get_field(f_name).get_type():
                raise SchemaValidationError(f'Invalid record field type for field {f_name} of type {self[f_name]}')
