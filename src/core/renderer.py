from jinja2 import Environment

from src.core.components.blueprint import Blueprint
from src.core.components.components import Component
from src.core.data.manifest import Record

from typing import Union


class Renderer:
    def __init__(self, config):
        self.env = Environment(autoescape=False)

    def render(self, element: Union[Component, Blueprint], record: Record) -> str:

        try:
            frame = element.get_frame()
        except AttributeError:
            template = self.env.from_string(element.get_template())
            context = {name: field.get_value(record) for name, field in element.get_field_dict().items()}

            if element.get_children() is not None:
                context['children'] = '\n'.join([self.render(child, record) for child in element.get_children()])
            return template.render(context)
        else:
            return self.render(frame, record)
