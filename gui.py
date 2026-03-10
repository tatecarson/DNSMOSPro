#!/usr/bin/env python3
"""Minimal GUI for DNSMOS Pro."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from cli import MODELS, default_device, score_audio_files


class DNSMOSProApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("DNSMOS Pro")
        self.root.geometry("980x760")
        self.root.minsize(900, 700)

        self.model_var = tk.StringVar(value="nisqa")
        self.device_var = tk.StringVar(value=default_device())
        self.recursive_var = tk.BooleanVar(value=True)
        self.verbose_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Choose files or a folder to begin.")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.selected_paths: list[str] = []

        self._build_layout()

    def _build_layout(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=2)
        frame.rowconfigure(4, weight=1)
        frame.rowconfigure(6, weight=1)

        ttk.Label(frame, text="DNSMOS Pro", font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            frame,
            text="Score speech quality from files or folders without using the terminal.",
        ).grid(row=1, column=0, sticky="w", pady=(4, 12))

        controls = ttk.Frame(frame)
        controls.grid(row=2, column=0, sticky="ew")

        ttk.Label(controls, text="Model").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            controls,
            textvariable=self.model_var,
            values=list(MODELS.keys()),
            state="readonly",
            width=12,
        ).grid(row=1, column=0, padx=(0, 12), sticky="w")

        ttk.Label(controls, text="Device").grid(row=0, column=1, sticky="w")
        ttk.Combobox(
            controls,
            textvariable=self.device_var,
            values=["cpu", "mps", "cuda"],
            state="readonly",
            width=12,
        ).grid(row=1, column=1, padx=(0, 12), sticky="w")

        ttk.Checkbutton(
            controls,
            text="Include subfolders",
            variable=self.recursive_var,
        ).grid(row=1, column=2, padx=(0, 12), sticky="w")

        ttk.Checkbutton(
            controls,
            text="Show variance",
            variable=self.verbose_var,
        ).grid(row=1, column=3, sticky="w")

        actions = ttk.Frame(frame)
        actions.grid(row=3, column=0, sticky="ew", pady=(14, 10))

        ttk.Button(actions, text="Add Files", command=self.add_files).pack(side="left")
        ttk.Button(actions, text="Add Folder", command=self.add_folder).pack(side="left", padx=8)
        ttk.Button(actions, text="Clear", command=self.clear_selection).pack(side="left")
        ttk.Button(actions, text="Run Scoring", command=self.run_scoring).pack(side="right")

        ttk.Label(frame, text="Selected inputs").grid(row=4, column=0, sticky="sw")
        selection_frame = ttk.Frame(frame)
        selection_frame.grid(row=5, column=0, sticky="nsew", pady=(4, 12))
        selection_frame.columnconfigure(0, weight=1)
        selection_frame.rowconfigure(0, weight=1)
        self.selection_box = tk.Text(selection_frame, height=7, wrap="none")
        self.selection_box.grid(row=0, column=0, sticky="nsew")
        selection_scroll = ttk.Scrollbar(selection_frame, orient="vertical", command=self.selection_box.yview)
        selection_scroll.grid(row=0, column=1, sticky="ns")
        selection_scroll_x = ttk.Scrollbar(
            selection_frame, orient="horizontal", command=self.selection_box.xview
        )
        selection_scroll_x.grid(row=1, column=0, sticky="ew")
        self.selection_box.configure(yscrollcommand=selection_scroll.set)
        self.selection_box.configure(xscrollcommand=selection_scroll_x.set)

        ttk.Label(frame, text="Results").grid(row=6, column=0, sticky="sw")
        results_frame = ttk.Frame(frame)
        results_frame.grid(row=7, column=0, sticky="nsew", pady=(4, 12))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        self.results_box = tk.Text(results_frame, height=14, wrap="none")
        self.results_box.grid(row=0, column=0, sticky="nsew")
        results_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_box.yview)
        results_scroll.grid(row=0, column=1, sticky="ns")
        results_scroll_x = ttk.Scrollbar(
            results_frame, orient="horizontal", command=self.results_box.xview
        )
        results_scroll_x.grid(row=1, column=0, sticky="ew")
        self.results_box.configure(yscrollcommand=results_scroll.set)
        self.results_box.configure(xscrollcommand=results_scroll_x.set)

        info_frame = ttk.LabelFrame(frame, text="Info", padding=12)
        info_frame.grid(row=0, column=1, rowspan=8, sticky="nsew", padx=(16, 0))
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        info_text = tk.Text(info_frame, wrap="word", width=34, height=24)
        info_text.grid(row=0, column=0, sticky="nsew")
        info_text.insert(
            "1.0",
            "Models\n"
            "nisqa: General-purpose MOS model. Best default choice for most student work.\n\n"
            "bvcc: Model trained on BVCC data. Useful if your audio is closer to voice conversion or synthetic speech tasks.\n\n"
            "vcc2018: Model trained on VCC2018 data. Good for experiments similar to that benchmark.\n\n"
            "Options\n"
            "Device: Usually leave this alone. mps uses Apple Silicon GPU, cuda uses NVIDIA GPU, cpu works everywhere.\n\n"
            "Include subfolders: Search through nested folders when you choose a directory.\n\n"
            "Show variance: Displays uncertainty alongside the MOS mean. Lower variance usually means the prediction is more confident.\n\n"
            "Typical interpretation\n"
            "Higher MOS means better perceived speech quality. Scores are most useful for comparing files under the same conditions."
        )
        info_text.configure(state="disabled")

        status_frame = ttk.Frame(frame)
        status_frame.grid(row=8, column=0, columnspan=2, sticky="ew")
        status_frame.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(4, 6))

        ttk.Label(status_frame, textvariable=self.status_var).grid(row=1, column=0, sticky="w")

    def add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.flac *.ogg *.m4a"),
                ("All files", "*.*"),
            ],
        )
        if paths:
            self.selected_paths.extend(str(Path(path)) for path in paths)
            self._refresh_selection()

    def add_folder(self) -> None:
        path = filedialog.askdirectory(title="Select a folder of audio files")
        if path:
            self.selected_paths.append(str(Path(path)))
            self._refresh_selection()

    def clear_selection(self) -> None:
        self.selected_paths = []
        self.selection_box.delete("1.0", "end")
        self.results_box.delete("1.0", "end")
        self.progress_var.set(0)
        self.status_var.set("Selection cleared.")

    def _refresh_selection(self) -> None:
        self.selected_paths = list(dict.fromkeys(self.selected_paths))
        self.selection_box.delete("1.0", "end")
        self.selection_box.insert("1.0", "\n".join(self.selected_paths))
        self.status_var.set(f"{len(self.selected_paths)} input(s) selected.")

    def run_scoring(self) -> None:
        if not self.selected_paths:
            messagebox.showerror("DNSMOS Pro", "Choose at least one file or folder first.")
            return

        self.results_box.delete("1.0", "end")
        self.status_var.set("Scoring in progress...")
        self.progress_var.set(0)
        threading.Thread(target=self._score_worker, daemon=True).start()

    def _score_worker(self) -> None:
        try:
            results = score_audio_files(
                self.selected_paths,
                model_name=self.model_var.get(),
                device=self.device_var.get(),
                recursive=self.recursive_var.get(),
                progress_callback=self._progress_callback,
            )
        except Exception as exc:
            self.root.after(0, lambda: self._show_error(str(exc)))
            return

        self.root.after(0, lambda: self._show_results(results))

    def _progress_callback(self, current: int, total: int, audio_file: Path) -> None:
        self.root.after(0, lambda: self._update_progress(current, total, audio_file))

    def _update_progress(self, current: int, total: int, audio_file: Path) -> None:
        percent = (current / total) * 100 if total else 0
        self.progress_var.set(percent)
        self.status_var.set(f"Scoring {current}/{total}: {audio_file.name}")

    def _show_error(self, message: str) -> None:
        self.status_var.set("Scoring failed.")
        self.progress_var.set(0)
        messagebox.showerror("DNSMOS Pro", message)

    def _show_results(self, results: list[tuple[Path, float, float]]) -> None:
        lines = []
        for audio_file, mean, variance in results:
            if self.verbose_var.get():
                lines.append(f"MOS={mean:.2f} (var={variance:.4f})  |  {audio_file}")
            else:
                lines.append(f"MOS={mean:.2f}  |  {audio_file}")

        self.results_box.insert("1.0", "\n".join(lines))
        self.progress_var.set(100)
        self.status_var.set(f"Finished scoring {len(results)} file(s).")


def main() -> None:
    root = tk.Tk()
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    DNSMOSProApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
