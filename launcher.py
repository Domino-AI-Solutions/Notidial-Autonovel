#!/usr/bin/env python3
"""
Advanced GUI Launcher for the Automatic-Writing Pipeline.

Features:
- Live log display for real-time feedback.
- Progress bar for visual tracking of tasks.
- Dedicated buttons for setup, server management, and all pipeline phases.
- Asynchronous process handling to keep the GUI responsive.
- Robust error handling and clear status updates.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import os
import sys
import queue
import shutil
import urllib.request
from pathlib import Path

# --- Venv Configuration ---
PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON_PATH = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"


class Backend:
    """Handles all backend process execution and server management."""

    def __init__(self, log_queue):
        self.log_queue = log_queue
        self.process = None
        self.is_cancelled = threading.Event()

    def log(self, message):
        self.log_queue.put(message)

    def run_command(self, command, on_complete=None, verbose=False):
        """Run a command with robust error handling and graceful exit."""
        
        if not command:
            return
        
        self.is_cancelled.clear()
        
        # Use atomic file operations to prevent conflicts
        script_file = Path(command[0]) if isinstance(command[0], str) else None
        
        def target():
            try:
                # Check if command is a path or executable name
                args_to_run = []
                if len(command) == 1:
                    args_to_run.append(command[0])
                elif all(isinstance(arg, str) for arg in command):
                    args_to_run = command
                
                self.log(f"--- Launching: {' '.join(args_to_run)} ---")
                
                # Use absolute paths to prevent file conflicts
                working_dir = Path.cwd()
                
                if script_file and not script_file.exists():
                    # Ensure parent directories exist for the target script
                    script_path = script_file.absolute()
                    script_dir = script_path.parent
                    if not os.path.exists(script_dir):
                        os.makedirs(script_dir, exist_ok=True)

                    self.log(f"Creating directory: {script_dir}")

                self.process = subprocess.Popen(
                    args_to_run,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    env=self._get_env(verbose),
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                    bufsize=1
                )

                for line in iter(self.process.stdout.readline, ''):
                    if self.is_cancelled.is_set():
                        self.log("[CANCELLED] Stop request received. Terminating process...")
                        self.process.terminate()
                        break
                    self.log(line.strip())

                self.process.wait()
                return_code = self.process.returncode

                if on_complete:
                    on_complete(return_code)

            except FileNotFoundError as e:
                # Handle missing command files gracefully
                error_msg = f"[ERROR] Command not found: {e.filename} or {command[0]}. Is it in your PATH?"
                self.log(error_msg)
                
            except subprocess.TimeoutExpired:
                # Timeout handling - cancel and clean up
                self.log("[ERROR] Process timed out. Terminating...")
                self.is_cancelled.set()
                try:
                    if on_complete:
                        on_complete(127)  # Return non-zero for timeout
                except:
                    pass
                if self.process:
                    self.process.terminate()
                if on_complete:
                    on_complete(124) # Standard exit code for timeout
                    
            except Exception as e:
                error_msg = f"[ERROR] Failed to run phase: {e}"
                self.log(error_msg)
                if on_complete:
                    on_complete(1)

        threading.Thread(target=target, daemon=True).start()
    
    def _get_env(self, verbose):
        env = os.environ.copy()
        env["AUTOWRITE_VERBOSE_LOGGING"] = "1" if verbose else "0"
        env["NON_INTERACTIVE"] = "1"
        return env


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Automatic Writing Pipeline")
        self.geometry("900x750")
        self.configure(bg="#1e1e1e")

        self.log_queue = queue.Queue()
        self.backend = Backend(self.log_queue)
        self.verbose_mode = tk.BooleanVar(value=False)

        self.create_widgets()
        self.after(100, self.process_log_queue)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        """Log a message to the logging queue."""
        self.log_queue.put(message)

    def process_log_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get_nowait()
            self.log_display.config(state=tk.NORMAL)
            self.log_display.insert(tk.END, message + '\n')
            self.log_display.see(tk.END)
            self.log_display.config(state=tk.DISABLED)
        self.after(100, self.process_log_queue)

    def start_task(self):
        if not self.backend.is_cancelled.is_set():
            self.progress.start(10)

        if not self.verbose_mode.get() and len(sys.argv) < 2:
            messagebox.showwarning("Missing Arguments", "This launcher requires a script path as an argument.")
            return
        
        is_verbose = self.verbose_mode.get()
        full_command = sys.argv[1:]

        self.backend.run_command(full_command, on_complete=self.end_task, verbose=is_verbose)

    def end_task(self, return_code=None):
        self.progress.stop()
        if return_code == 0:
            self.log("[INFO] Pipeline has completed gracefully.")
        elif self.backend.is_cancelled.is_set():
            self.log("[INFO] Task was cancelled by user.")
        else:
            self.log(f"[FAIL] Task exited with code {return_code}.")

        # After a task completes (successfully, cancelled, or failed),
        # ask the user if they want to quit the application.
        if messagebox.askokcancel("Quit", "The pipeline has finished, but the window is still open. Do you want to quit?"):
            self.stop_task()
            self.destroy()

    def get_fastsd_dir(self):
        yaml_path = PROJECT_ROOT / "configuration.yaml"
        if yaml_path.exists():
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("fastsd_dir:"):
                            val = line.split(":", 1)[1].strip()
                            val = val.strip('"').strip("'")
                            val = val.replace("\\\\", "\\")
                            return Path(val)
            except Exception as e:
                self.log(f"[WARN] Failed to parse configuration.yaml: {e}")
        return PROJECT_ROOT.parent / "fastsdcpu"

    def update_fastsd_dir(self, new_dir):
        yaml_path = PROJECT_ROOT / "configuration.yaml"
        lines = []
        updated = False
        if yaml_path.exists():
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("fastsd_dir:"):
                            escaped_path = str(new_dir).replace("\\", "\\\\")
                            lines.append(f'fastsd_dir: "{escaped_path}"\n')
                            updated = True
                        else:
                            lines.append(line)
            except Exception as e:
                self.log(f"[WARN] Failed to read configuration.yaml: {e}")

        if not updated:
            escaped_path = str(new_dir).replace("\\", "\\\\")
            lines.append(f'fastsd_dir: "{escaped_path}"\n')
        
        try:
            with open(yaml_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            self.log(f"[INFO] Updated fastsd_dir in configuration.yaml to {new_dir}")
        except Exception as e:
            self.log(f"[ERROR] Failed to save configuration.yaml: {e}")

    def check_and_run_action(self, script_path, mode):
        is_verbose = self.verbose_mode.get()

        # 1. Check Python Venv
        if mode in ["seed", "foundation", "draft", "revise", "audit", "audiobook", "full"]:
            if not VENV_PYTHON_PATH.exists():
                if messagebox.askyesno("Setup Required", "The virtual environment was not found. Would you like to run setup.bat now?"):
                    self.run_action("setup.bat", "setup")
                    # Do NOT return — setup runs async in the log; the user must
                    # click the button again once setup finishes.
                return

            # Only check core packages — audiobook/TTS checks itself at runtime
            # and prints a clear error. We never block audiobook here.
            try:
                python_exe = str(VENV_PYTHON_PATH)
                subprocess.run(
                    [python_exe, "-c", "import dotenv, httpx, yaml"],
                    check=True, capture_output=True
                )
            except subprocess.CalledProcessError:
                msg = (
                    "Core packages (dotenv, httpx, PyYAML) appear to be missing.\n"
                    "Would you like to run setup.bat now to install them?"
                )
                if messagebox.askyesno("Setup Required", msg):
                    self.run_action("setup.bat", "setup")
                return

        # 2. Check Audiobook dependencies (Piper)
        if mode == "audiobook":
            try:
                python_exe = str(VENV_PYTHON_PATH)
                subprocess.run([python_exe, "-c", "from piper.voice import PiperVoice"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                msg = ("The 'piper-tts' package seems to be missing from the project's virtual environment.\n\n"
                       "Would you like to run 'First-Time Setup' now to install it?")
                if messagebox.askyesno("TTS Dependency Missing", msg):
                    self.run_action("setup.bat", "setup")
                return

        # 3. Check Ollama server status (for LLM tasks)
        if mode in ["seed", "foundation", "draft", "revise", "audit", "full"]:
            ollama_running = False
            try:
                with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.5) as response:
                    if response.getcode() == 200:
                        ollama_running = True
            except Exception:
                pass

            if not ollama_running:
                if messagebox.askyesno("Ollama Offline", "The local Ollama server does not seem to be running. Would you like to start it now?"):
                    self.log("[INFO] Launching Ollama server...")
                    subprocess.Popen(["cmd", "/c", "start \"Ollama Server\" ollama serve"])
                    self.log("[INFO] Ollama server command sent. Waiting a moment to initialize...")
                    self.after(3000, lambda: self.run_action(script_path, mode))
                    return
                else:
                    self.log("[WARN] Attempting to run task while Ollama server is offline.")

        # 4. Check Pandoc for manuscript export
        if mode == "export":
            pandoc_installed = False
            try:
                subprocess.run(["pandoc", "--version"], check=True, capture_output=True)
                pandoc_installed = True
            except Exception:
                pass

            if not pandoc_installed:
                msg = "Pandoc was not found in your system PATH.\n\nWithout Pandoc, manuscript export will only combine the markdown chapters but cannot generate PDF or ePub files.\n\nWould you like to run the markdown combiner anyway?"
                if not messagebox.askyesno("Pandoc Missing", msg):
                    self.log("[INFO] Export cancelled. Please install Pandoc.")
                    return

        # Fallthrough to running standard actions
        self.run_action(script_path, mode)


    def stop_task(self):
        self.log("[INFO] Sending stop request to current task...")
        self.backend.is_cancelled.set()

    def run_action(self, script_path, mode):
        is_verbose = self.verbose_mode.get()

        # Determine the command based on file type
        if script_path and script_path.endswith(".bat"):
            command = [script_path]
            self.log(f"--- Launching batch file: {script_path} ---")
            self.progress.start(10)
            self.backend.run_command(command, on_complete=self.end_task, verbose=is_verbose)
        elif script_path:
            # Use the venv python if it exists, otherwise fall back to the system python
            python_exe = str(VENV_PYTHON_PATH) if VENV_PYTHON_PATH.exists() else "python"
            # This handles all python scripts
            command = [python_exe, "-u", script_path]
            if mode in ["draft", "audiobook"]:
                self.show_chapter_dialog(mode, command)
            elif mode == "full":
                full_cmd = command + ["--phase", "full"]
                self.log(f"[INFO] Running full pipeline: {' '.join(full_cmd)}")
                self.progress.start(10)
                self.backend.run_command(full_cmd, on_complete=self.end_task, verbose=is_verbose)
            else: # For all other python scripts (seed, foundation, revise, audit, art, export)
                self.log(f"[INFO] Running {mode} script.")
                self.progress.start(10)
                self.backend.run_command(command, on_complete=self.end_task, verbose=is_verbose)

    def show_chapter_dialog(self, mode, base_command):
        title = "Draft Chapter" if mode == "draft" else "Generate Audiobook"
        
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("320x150")
        dialog.configure(bg="#2a2a2a")
        dialog.transient(self)
        dialog.grab_set()

        # Add chapter number entry for draft mode only
        if mode == "draft":
            label = tk.Label(dialog, text="Chapter Number:", bg="#2a2a2a", fg="white").pack(pady=10)
            entry = tk.Entry(dialog, width=10)
            entry.pack(pady=5)
            entry.insert(0, "1")

            def on_run():
                chapter_num_str = entry.get()
                if not chapter_num_str.isdigit():
                    self.log("[ERROR] Invalid chapter number.")
                    return

                command = base_command + ["--chapter", chapter_num_str]
                is_verbose = self.verbose_mode.get()
                
                self.progress.start(10)
                self.backend.run_command(command, on_complete=self.end_task, verbose=is_verbose)
                dialog.destroy()

            run_btn = ttk.Button(dialog, text="Run", command=on_run)
            run_btn.pack(pady=15)
        else: # audiobook
            label = tk.Label(dialog, text="Chapter Number (0 for all):", bg="#2a2a2a", fg="white").pack(pady=10)
            
            entry = tk.Entry(dialog, width=15)
            entry.pack(pady=5)
            entry.insert(0, "0")

            def on_run():
                chapter_num_str = entry.get()
                
                if not chapter_num_str.isdigit():
                    self.log("[ERROR] Invalid chapter number.")
                    return

                if chapter_num_str == "0":
                    command = base_command
                else:
                    command = base_command + ["--chapter", chapter_num_str]
                
                is_verbose = self.verbose_mode.get()
                
                self.progress.start(10)
                self.backend.run_command(command, on_complete=self.end_task, verbose=is_verbose)
                dialog.destroy()

            run_btn = ttk.Button(dialog, text="Run", command=on_run)
            run_btn.pack(pady=15)

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel for controls
        control_panel = tk.Frame(main_frame, bg="#2a2a2a", width=250)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_panel.pack_propagate(False)

        # Right panel for logs
        log_panel = tk.Frame(main_frame, bg="#2a2a2a")
        log_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Control Panel Widgets ---
        tk.Label(control_panel, text="Pipeline Control", font=("Helvetica", 16, "bold"), fg="#00ddff", bg="#2a2a2a").pack(pady=15)

        buttons = [
            ("First-Time Setup", "setup.bat", "setup"),
            ("Launch Servers", "start_servers.bat", "servers"),
            ("Generate Seed", "scripts/generate_seed.py", "seed"),
            ("Build Foundation", "scripts/build_foundation.py", "foundation"),
            ("Draft Chapter", "scripts/draft_chapter.py", "draft"),
            ("Revise Weak Chapters", "scripts/revise_all_weak_chapters.py", "revise"),
            ("Run Full Audit", "scripts/anti_slop.py", "audit"),
            ("Generate Art", "scripts/gen_cover_art.py", "art"),
            ("Generate Audiobook", "scripts/gen_audiobook.py", "audiobook"),
            ("Export Manuscript", "scripts/export.py", "export"),
            ("Run Full Pipeline", "run_pipeline.py", "full")
        ]

        for text, script, mode in buttons:
            btn = ttk.Button(control_panel, text=text, command=lambda s=script, m=mode: self.check_and_run_action(s, m))
            btn.pack(pady=6, padx=20, fill=tk.X)

        # Stop button and verbose checkbox at the bottom
        ttk.Separator(control_panel, orient='horizontal').pack(fill='x', pady=10, padx=20)
        
        self.stop_button = ttk.Button(control_panel, text="Stop Current Task", command=self.stop_task)
        self.stop_button.pack(pady=5, padx=20, fill=tk.X)

        ttk.Checkbutton(control_panel, text="Verbose Logging", variable=self.verbose_mode).pack(pady=10)

        # --- Log Panel Widgets ---
        tk.Label(log_panel, text="Live Log", font=("Helvetica", 16, "bold"), fg="white", bg="#2a2a2a").pack(pady=(15, 5))

        self.progress = ttk.Progressbar(log_panel, mode='indeterminate')
        self.progress.pack(pady=(0, 10), fill=tk.X, padx=10)

        log_frame = tk.Frame(log_panel, bg="black")
        log_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.log_display = scrolledtext.ScrolledText(log_frame, state=tk.DISABLED, bg="black", fg="lightgray", font=("Consolas", 10), relief=tk.FLAT, bd=0)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="#3c3c3c", foreground="white")
        style.map("TButton", background=[('active', '#0078d7')])
        style.configure("TProgressbar", thickness=5, background='#0078d7', troughcolor='#3c3c3c')

    def on_closing(self):
        if self.backend.process and self.backend.process.poll() is None:
            if messagebox.askokcancel("Quit", "A task is still running. Do you want to stop it and quit?"):
                self.backend.is_cancelled.set()
                self.destroy()
        else:
            self.destroy()


def main():
    """Main launcher entry point"""
    
    # Initialize log display at startup
    app = App()
    
    # Add event handlers for graceful cleanup
    # app.protocol("WM_DELETE_WINDOW", app.on_closing) # Already set in __init__
    
    app.mainloop()


if __name__ == "__main__":
    main()
