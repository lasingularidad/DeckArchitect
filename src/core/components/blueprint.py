from pathlib import Path
import yaml

from src.core.data.schema import DataSchema
from src.core.data.fields import Reference
from src.core.exceptions import SchemaValidationError

from typing import Dict, Any


class Blueprint:

    @classmethod
    def load(cls, file_path: Path, registry: "ComponentRegistry"):
        with (open(file_path, 'r') as layout_fp):
            loader = yaml.SafeLoader(layout_fp)
            loader.add_multi_constructor(u'!Comp:', registry.component_instance_constructor)
            loader.add_constructor(u'!Ref', Reference.from_yaml_node)
            data = loader.get_single_data()

            field_names= [field['name'] for field in data['schema']]
            field_types = [field['type'] for field in data['schema']]
            data['schema'] = DataSchema(field_names, field_types)

            frame_instance = registry.get_frame()
            frame_instance.update_values(data['frame'])
            data['frame'] = frame_instance

            return cls(data)

    def __init__(self, blueprint_data: Dict[str, Any]):
        self._name = blueprint_data['name']
        self._description = blueprint_data['description']
        self._schema = blueprint_data['schema']
        self._frame: Component = blueprint_data['frame']

        self._schema.validate_component(self._frame)

    def get_frame(self):
        return self._frame

    def get_schema(self):
        return self._schema

    """@classmethod
    def _component_from_node(cls, loader: yaml.Loader, tag_suffix, node):
        component = self.get_component(tag_suffix)
        value_map = loader.construct_mapping(node, deep=True)
        component.update_values(value_map)
        return component

    @classmethod
    def _get_reference_loader(cls, schema:DataSchema):
        def load_reference_from_node(loader: yaml.Loader, node):
            # Check reference is valid
            target = loader.construct_scalar(node)
            if not target in schema.keys():
                raise SchemaValidationError(f'Reference target {target} is not present in blueprint data schema')
            ref = Reference(target)
            ref.set_type(schema[target])
            return ref
        return load_reference_from_node"""


    """def render(self, jinja_env: Environment, card: Dict[str, Any]) -> str:
        return self._frame.render(jinja_env, card)"""


if __name__ == "__main__":
    from src.core.data.manifest import Record
    from src.core.components.registry import ComponentRegistry, RegistryConfig
    from src.core.renderer import Renderer

    reg_config = RegistryConfig()
    reg_config.directory = Path('../../../assets/components/')
    reg = ComponentRegistry(reg_config)

    test_template = Blueprint.load(Path('../../../assets/examples/sample_blueprint.yml'), reg)

    renderer = Renderer(None)
    record = Record(test_template.get_schema(), ["Given title", "images/frameTexture01.png", 10])
    with open('../../../output/index.html', 'wt') as fp:
        fp.write(renderer.render(test_template, record))