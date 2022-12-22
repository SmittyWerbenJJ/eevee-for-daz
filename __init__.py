# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import importlib
from pathlib import Path

bl_info = {
    "name": "Eevee for Daz",
    "author": "SmittyWerbenHD",
    "description": "Fast eevee material setup for daz characters",
    "blender": (3, 3, 0),
    "version": (0, 0, 2),
    "location": "",
    "warning": "",
    "category": "Generic"
}

# ---------------------------------------------
# auto-load modules from sibling files
# import modules in this directory
# ---------------------------------------------
moduleNames = []
ignoredModules = [
    Path(__file__).name,
    "__init__.py",
    "easybpy.py"
]
for file in Path(__file__).parent.glob("*.py"):
    globfile = Path(file)
    if globfile.name in ignoredModules:
        continue
    moduleNames.append(file.stem)

# ui module has to be loaded first
moduleNames.insert(0, moduleNames.pop(moduleNames.index("ui")))

anchor = Path(__file__).parent.name
modules = []
for moduleName in moduleNames:
    mod = importlib.import_module("." + moduleName, anchor)
    modules.append(mod)

# ---------------------------------------------
# Blender Register
# ---------------------------------------------


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
