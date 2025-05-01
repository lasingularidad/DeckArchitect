import unittest
import csv
from io import StringIO

from src.core.data.manifest import CardManifest, Record
from src.core.data.schema import DataSchema
from src.core.data.fields import FieldType
from src.core.exceptions import SchemaValidationError


class TestRecord(unittest.TestCase):
    def setUp(self):
        self.schema = DataSchema(
            ['title', 'color'],
            [FieldType.TEXT, FieldType.COLOR]
        )

    def test_record_initialization(self):
        record = Record(self.schema, ['Dragon', '#FF0000'])
        self.assertEqual(record.get_field('title').get_value(), 'Dragon')
        self.assertEqual(record.get_field('title').get_type(), FieldType.TEXT)
        self.assertEqual(record.get_field('color').get_value(), '#FF0000')
        self.assertEqual(record.get_field('color').get_type(), FieldType.COLOR)

    def test_get_field_values(self):

        record = Record(self.schema, ['Dragon', '#FF0000'])
        values = record.get_field_values()
        self.assertEqual(str(values['title']), 'Dragon')
        self.assertEqual(str(values['color']), '#FF0000')

    def test_get_field(self):
        record = Record(self.schema, ['Dragon', '#FF0000'])
        self.assertEqual(record.get_field('title').get_value(), 'Dragon')
        self.assertEqual(record.get_field('title').get_type(), FieldType.TEXT)

        with self.assertRaises(KeyError):
            record.get_field('nonexistent_field')

    def test_initialization_error(self):
        # Missing fields
        with self.assertRaises(SchemaValidationError) as context:
            Record(self.schema, ['OnlyOneField'])
        self.assertIn('Number of input fields (1) is not equal to number of expected fields (2)', str(context.exception))

        # Extra fields
        with self.assertRaises(SchemaValidationError) as context:
            Record(self.schema, ['Dragon', '#FF0000', 'ExtraField'])
        self.assertIn('Number of input fields (3) is not equal to number of expected fields (2)', str(context.exception))

        # Invalid number
        schema = DataSchema(['damage'], [FieldType.NUMBER])
        with self.assertRaises(ValueError) as context:
            Record(schema, ['not-a-number'])
        self.assertIn('could not convert string to float', str(context.exception))

        # Invalid color
        schema = DataSchema(['color'], [FieldType.COLOR])
        with self.assertRaises(ValueError) as context:
            Record(schema, ['red'])
        self.assertEqual('Value "red" is not a valid hexadecimal color string', str(context.exception))

        # Invalid measure
        schema = DataSchema(['size'], [FieldType.MEASURE])
        with self.assertRaises(TypeError) as context:
            Record(schema, ['50ptr'])
        self.assertIn('Unrecognized measure type for input "50ptr"', str(context.exception))


class TestCardManifest(unittest.TestCase):
    def test_csv_manifest_creation(self):
        csv_data = StringIO("""name,power
text,number
Fireball,10
Ice Bolt,8
""")
        reader = csv.reader(csv_data)
        manifest = CardManifest.from_iterator('spells', reader)
        self.assertEqual(len(manifest._records), 2)
        self.assertListEqual(list(manifest._schema.get_field_names()), ['name', 'power'])
        self.assertEqual(manifest._records[0].get_field_values()['name'], 'Fireball')

    def test_invalid_manifest(self):
        csv_data = StringIO("""name,power
text,number
Fireball
""")
        reader = csv.reader(csv_data)
        with self.assertRaises(SchemaValidationError):
            CardManifest.from_iterator('broken', reader)

    def test_special_characters(self):
        csv_data = StringIO("""title,description
text,text
"Chaos, Lord","Contains, comma"
""")
        reader = csv.reader(csv_data)
        manifest = CardManifest.from_iterator('special', reader)
        record = manifest._records[0]
        self.assertEqual(record.get_field('title').get_value(), 'Chaos, Lord')
        self.assertEqual(record.get_field('description').get_value(), 'Contains, comma')

    def test_empty_manifest(self):
        csv_data = StringIO("""name
""")
        reader = csv.reader(csv_data)
        with self.assertRaises(ValueError):
            CardManifest.from_iterator('empty', reader)


if __name__ == '__main__':
    unittest.main()
