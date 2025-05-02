from pathlib import Path
import csv

from src.core.data.schema import DataSchema

from typing import List, Iterator


class Record:

    def __init__(self, schema: DataSchema=None, values: List[str]=None):
        self._schema = schema or DataSchema([],[])
        values = values or []
        fields = self._schema.populate_fields(values)
        self._data = dict(zip(self._schema.keys(), fields))

    def get_field_names(self):
        return self._data.keys()

    def get_field_values(self) -> dict:
        """Convenience method for test assertions.
        Returns a dict of field names and their values."""
        return {name: field.get_value() for name, field in self._data.items()}

    def get_field(self, field_name: str):
        return self._data[field_name]

    def validate_reference(self, target, f_type):
       self._schema.validate_reference(target, f_type)


class CardManifest:

    @classmethod
    def from_csv(cls, name: str, set_file: Path):
        with open(set_file, 'r') as set_fp:
            return cls.from_iterator(name, csv.reader(set_fp))

    @classmethod
    def from_iterator(cls, name: str, reader: Iterator):
        """New method to accept any iterable for testing"""
        try:
            field_names = next(reader)
            field_types = next(reader)
        except StopIteration:
            raise ValueError('Input data does not contain schema definition.')
        schema = DataSchema(field_names, field_types)
        records = [Record(schema, entry) for entry in reader]
        return cls(name, schema, records)

    def __init__(self, name: str, schema: DataSchema, records: List["Record"]):
        self._name = name

        self._schema = schema

        self._validate_records(records)
        self._records = records

    def _validate_records(self, records):
        for record in records:
            self._schema.validate_record(record)


if __name__ == "__main__":

    manifest = CardManifest.from_csv('test', Path('../../../assets/examples/sample_manifest.csv'))
    print(manifest)
