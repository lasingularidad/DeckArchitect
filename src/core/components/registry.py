from pathlib import Path
from copy import deepcopy
from dataclasses import dataclass

import yaml

from src.core.components.components import Component

from typing import Dict


class RegistryConfig:
    directory: Path
    pattern: str = '*.cmp.yml'
    frame_file: str = 'cardframe.frame.yml'


class ComponentRegistry:
    """Manages loading and accessing component types"""

    def __init__(self, config: RegistryConfig):
        self._config = config
        self.definitions: Dict[str, Component] = {}

        self._load_components()

    def _load_components(self):
        self._frame = Component.load_definition(self._config.directory / self._config.frame_file)
        if not self._config.directory.is_dir():
            raise NotADirectoryError(f'Cannot load components. "{self._config.directory}" is not a directory.')
        for cmp_file in self._config.directory.glob(self._config.pattern):
            component = Component.load_definition(cmp_file)
            self.definitions[component.get_type()] = component

    def get_frame(self) -> Component:
        return deepcopy(self._frame)

    def get_component(self, component_type: str) -> Component:
        return deepcopy(self.definitions[component_type])

    def component_instance_constructor(self, loader: yaml.Loader, tag_suffix, node):
        component = self.get_component(tag_suffix)
        value_map = loader.construct_mapping(node, deep=True)
        component.update_values(value_map)
        return component
