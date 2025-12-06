"""
TDCT – Trial Design Consistency Testing

Core package initialisation.
"""

from .runner import TDCTRunner, run_tdct
from .utils import load_protocol, save_json

__all__ = [
    "TDCTRunner",
    "run_tdct",
    "load_protocol",
    "save_json",
]

__version__ = "1.0.0"
