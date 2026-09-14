#!/usr/bin/env python3
"""
Run logger for the Automatic-Writing Pipeline.

Creates timestamped log files in the 'logs/' directory for every
pipeline run, close, or crash. Each log entry includes a date and
time stamp so issues can be traced precisely.
"""

import os
from datetime import datetime
from pathlib import Path


class RunLogger:
    """Manages dedicated log files for each pipeline run."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_log_file: Path | None = None
        self._file_handle = None
        self._run_start: datetime | None = None

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def start_run(self, run_name: str = "") -> Path:
        """Open a new log file and record the run start."""
        self._close_existing()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = run_name.strip().replace(" ", "_") if run_name else "run"
        filename = f"{timestamp}_{safe_name}.log"
        self.current_log_file = self.log_dir / filename
        self._file_handle = open(self.current_log_file, "w", encoding="utf-8")
        self._run_start = datetime.now()
        self._write_line("=" * 60)
        self._write_line(f"  Pipeline Run Started  —  {self._run_start.isoformat()}")
        self._write_line("=" * 60)
        self._flush()
        return self.current_log_file

    def log(self, message: str) -> str:
        """Write a timestamped message to the current log file.

        Returns the timestamped string so callers can also display it.
        """
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {message}"
        if self._file_handle and not self._file_handle.closed:
            self._file_handle.write(line + "\n")
            self._flush()
        return line

    def end_run(self, status: str = "completed") -> None:
        """Record the run end and close the log file."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._write_line("-" * 60)
        self._write_line(f"  Pipeline Run {status}  —  {ts}")
        if self._run_start:
            duration = datetime.now() - self._run_start
            self._write_line(f"  Duration: {duration}")
        self._write_line("=" * 60)
        self._write_line("")
        self._flush()
        self._close_existing()

    # ------------------------------------------------------------------ #
    #  Internals                                                           #
    # ------------------------------------------------------------------ #

    def _write_line(self, line: str) -> None:
        if self._file_handle and not self._file_handle.closed:
            self._file_handle.write(line + "\n")

    def _flush(self) -> None:
        if self._file_handle and not self._file_handle.closed:
            self._file_handle.flush()

    def _close_existing(self) -> None:
        if self._file_handle and not self._file_handle.closed:
            try:
                self._file_handle.close()
            except Exception:
                pass
        self._file_handle = None
        self.current_log_file = None
        self._run_start = None

    # ------------------------------------------------------------------ #
    #  Convenience / singleton-like access                                 #
    # ------------------------------------------------------------------ #

    _instance: "RunLogger | None" = None

    @classmethod
    def get(cls, log_dir: str = "logs") -> "RunLogger":
        """Return a module-level singleton so any file can log easily."""
        if cls._instance is None:
            cls._instance = cls(log_dir)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Clear the singleton (useful for testing)."""
        cls._instance = None
