from typing import TYPE_CHECKING
import logging
import argparse

from sphinx.util import logging
from peakrdl.config.loader import load_cfg
from peakrdl.plugins.importer import get_importer_plugins

from . import design_state as DS

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config

log = logging.getLogger("config")

def setup_config(app: "Sphinx") -> None:
    # Compilation settings
    app.add_config_value("peakrdl_cfg_toml", None, "env", [str])
    app.add_config_value("peakrdl_input_files", [], "env", [list])
    app.add_config_value("peakrdl_incdirs", [], "env", [list])
    app.add_config_value("peakrdl_parameters", {}, "env", [dict])
    app.add_config_value("peakrdl_defines", {}, "env", [dict])
    app.add_config_value("peakrdl_top_component", None, "env", [str])

    app.add_config_value("peakrdl_default_link_to", "html", "env", [str])

    # Control PeakRDL-html output
    app.add_config_value("peakrdl_html_enable", True, "env", [bool])
    app.add_config_value("peakrdl_html_title", None, "env", [str])
    app.add_config_value("peakrdl_html_extra_doc_properties", [], "env", [list])

    # Inline doc settings
    app.add_config_value("peakrdl_doc_wrap_section", True, "env", [bool])

    # Support UDPs
    app.add_config_value("peakrdl_udps", [], "env", [list])


def elaborate_config_callback(app: "Sphinx", cfg: "Config") -> None:
    # Load PeakRDL configuration
    DS.peakrdl_cfg = load_cfg(cfg.peakrdl_cfg_toml)
    DS.importers = get_importer_plugins(DS.peakrdl_cfg)

    # Make a dummy argparse options namespace to satisfy importer plugins
    arg_parser = argparse.ArgumentParser()
    for importer in DS.importers:
        importer_arg_group = arg_parser.add_argument_group(importer.name)
        importer.add_importer_arguments(importer_arg_group)
    DS.argparse_options = arg_parser.parse_args([])

    # transform defines of key:None --> key:""
    new_defines = {}
    for key, value in cfg.peakrdl_defines.items():
        if value is None:
            new_defines[key] = ""
        else:
            new_defines[key] = value
    cfg.peakrdl_defines = new_defines

    # Validate
    if cfg.peakrdl_default_link_to not in {"doc", "html"}:
        raise ValueError("Config 'peakrdl_default_link_to' shall be either 'doc' or 'html")
