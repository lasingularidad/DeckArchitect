import unittest
from pathlib import Path

from src.core.data.fields import Field, FieldType, FieldValidationError


class TestFields(unittest.TestCase):
    def setUp(self):
        self.schema = None

    def test_editable(self):
        field = Field(FieldType.TEXT, editable= True, value='test')
        self.assertEqual(field.get_value(), 'test')
        field.set_value('other')
        self.assertEqual(field.get_value(),'other')

        field = Field(FieldType.TEXT, editable=False, value='fixed')
        self.assertEqual(field.get_value(), 'fixed')
        with self.assertRaises(FieldValidationError):
            field.set_value('other')

    def test_type_validation(self):
        field = Field(FieldType.MEASURE, editable=True, value='5mm')
        with self.assertRaises(FieldValidationError):
            field.set_value(12)

        field = Field(FieldType.NUMBER, editable=True, value=12)
        with self.assertRaises(FieldValidationError):
            field.set_value('some text')
        with self.assertRaises(FieldValidationError):
            field.set_value(Path('./myPath'))


if __name__ == '__main__':
    unittest.main()
