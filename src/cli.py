from pathlib import Path
import argparse

from jinja2 import Environment

from src.core.components.components import Component, ComponentRegistry

parser = argparse.ArgumentParser()
parser.add_argument("--components")
parser.add_argument("--texture")

args = parser.parse_args()
comp_path = Path(args.components)
texture_path = comp_path / args.texture

frame = Component.load_definition(comp_path / 'cardframe.frame.yml')

reg = ComponentRegistry()
reg.load_from_directory(comp_path)
box = reg.get_component('Box')
box.set_field('height', '50%')
box.set_field('border_width', '0mm')

image = reg.get_component('Image')
image.set_field('src', texture_path)

box.add_child(image)
box.add_child(reg.get_component('Text'))
frame.add_child(box)

env = Environment()
with open('../../output/index.html', 'wt') as fp:
    fp.write(frame.render(env, None))
