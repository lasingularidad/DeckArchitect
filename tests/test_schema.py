import unittest


from src.core.data.manifest import Record
from src.core.data.schema import DataSchema
from src.core.data.fields import FieldType
from src.core.exceptions import SchemaValidationError

class TestDataSchemaValidation(unittest.TestCase):
    def test_valid_schema_validation(self):
        schema = DataSchema(
            field_names=['name', 'power'],
            field_types=[FieldType.TEXT, FieldType.NUMBER]
        )
        valid_record = Record(schema, ['Fireball', '10'])
        schema.validate_record(valid_record)  # Should not raise

        reverse_schema = DataSchema(
            field_names=['power', 'name'],
            field_types=[FieldType.NUMBER, FieldType.TEXT]
        )
        valid_record = Record(reverse_schema, ['10', 'Ice'])
        schema.validate_record(valid_record)  # Should not raise

    def test_invalid_schema_validation(self):

        record_schema = DataSchema(
            field_names=['name', 'power'],
            field_types=[FieldType.TEXT, FieldType.NUMBER]
        )
        invalid_record = Record(record_schema, ['Ice', '15'])

        # Expect validation error when not all fields from schema
        # and record have the same type
        validating_chema = DataSchema(
            field_names=['name', 'power'],
            field_types=[FieldType.TEXT, FieldType.TEXT]
        )
        with self.assertRaises(SchemaValidationError):
            validating_chema.validate_record(invalid_record)

        # Expect validation error when some fields present in the schema
        # are not preset in the record
        validating_chema = DataSchema(
            field_names=['name', 'power', 'owner'],
            field_types=[FieldType.TEXT, FieldType.NUMBER, FieldType.TEXT]
        )
        with self.assertRaises(SchemaValidationError):
            validating_chema.validate_record(invalid_record)

        # Expect validation error when some fields present in the record
        # are not preset in the schema
        validating_chema = DataSchema(
            field_names=['name', ],
            field_types=[FieldType.TEXT]
        )
        with self.assertRaises(SchemaValidationError):
            validating_chema.validate_record(invalid_record)