from typing import TYPE_CHECKING, List

from sphinx.util import logging
from systemrdl import RDLCompiler
from systemrdl.messages import RDLCompileError
from peakrdl.process_input import load_file

from . import design_state as DS
from .utils import status_iterator, progress_message

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

log = logging.getLogger("config")

def compile_input_callback(app: "Sphinx", env: "BuildEnvironment", docnames: List[str]) -> None:
    """
    Called by the 'env-before-read-docs' event.

    Compile/import and elaborate all input
    """
    rdlc = RDLCompiler()

    for udp_cls in app.config.peakrdl_udps:
        rdlc.register_udp(udp_cls, soft=False)

    files = app.config.peakrdl_input_files
    if not files:
        return
    for file in status_iterator(files, "Reading PeakRDL sources...", length=len(files)):
        try:
            load_file(
                rdlc,
                DS.importers,
                file,
                app.config.peakrdl_defines,
                app.config.peakrdl_incdirs,
                DS.argparse_options,
            )
        except RDLCompileError as e:
            log.error("Failed when reading file: %s", file)
            raise e

    with progress_message("Elaborating PeakRDL design"):
        try:
            root = rdlc.elaborate(
                top_def_name=app.config.peakrdl_top_component,
                inst_name=None,
                parameters=app.config.peakrdl_parameters,
            )
            DS.root_node = root
        except RDLCompileError as e:
            log.error("Failed to elaborate PeakRDL design")
            raise e
