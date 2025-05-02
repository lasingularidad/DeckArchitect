from pathlib import Path

import yaml

from src.core.data.fields import Field
from src.core.data.schema import DataSchema
from src.core.exceptions import ComponentError

from typing import Dict, Any


class Component:

    @classmethod
    def load_definition(cls, file_path: Path):
        with open(file_path, 'r') as file_pointer:
            component_def = yaml.safe_load(file_pointer)
        return cls(component_def)

    def __init__(self, component_def: Dict[str, Any]):
        self._type = component_def['type']
        self._description = component_def['description']
        self._fields = self._build_fields(component_def['fields'])
        self._jinja = component_def['jinja']
        if not component_def.get('is_container', False):
            self._children = None
        else:
            self._children = []

    def get_type(self):
        return self._type

    def get_field(self, field_name):
        return self._fields[field_name].get_value()

    def get_field_dict(self):
        return self._fields

    def set_field(self, field_name, new_value):
        self._fields[field_name].set_value(new_value)

    def add_child(self, child):
        if self._children is None:
            raise ComponentError('Trying to add a child to a non container component.')
        else:
            self._children.append(child)

    def get_children(self):
        return self._children

    def update_values(self, new_values: Dict[str, Any]):
        for field_name, value in new_values.items():
            if field_name == 'children':
                for child in value:
                    self.add_child(child)
            else:
                self.set_field(field_name, value)

    def get_template(self):
        return self._jinja

    def get_schema(self):
        schema_fields = [field for field in self._fields.values() if field.is_reference()]
        target_names = [field.get_target() for field in schema_fields]
        field_types = [field.get_type() for field in schema_fields]
        schema = DataSchema(target_names, field_types)
        if self._children is not None:
            for child in self._children:
                schema.update(child.get_schema())
        return schema

    """ def render(self, my_env: Environment, card: Dict[str, Any]) -> str:
        template = my_env.from_string(self._jinja)
        context = {name: field.get_value(card) for name, field in self._fields.items()}
        if self._children is not None:
            context['children'] = '\n'.join([child.render(my_env, card) for child in self._children])
        return template.render(context)"""

    @staticmethod
    def _build_fields(field_data: Dict[str, Dict[str, Any]]):
        field_dict = {}
        for name, data in field_data.items():
            value_type = data['type']
            editable = data.get('editable', False)
            value = data['default']
            field_dict[name] = Field(value_type, editable, value)
        return field_dict

    def __repr__(self):
        return self._description


if __name__ == "__main__":

    from src.core.components.registry import ComponentRegistry, RegistryConfig
    from src.core.renderer import Renderer

    reg_config = RegistryConfig()
    reg_config.directory = Path('../../../assets/components/')
    reg = ComponentRegistry(reg_config)

    frame = reg.get_frame()

    box = reg.get_component('Box')
    box.set_field('height', '50%')
    box.set_field('border_width', '0mm')

    image = reg.get_component('Image')
    image.set_field('src', './frameTexture01.png')

    box.add_child(image)
    box.add_child(reg.get_component('Text'))
    frame.add_child(box)

    renderer = Renderer(None)
    with open('../../../output/index.html', 'wt') as fp:
        fp.write(renderer.render(frame, None))
