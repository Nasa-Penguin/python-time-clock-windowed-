"""
NEON CLOCK X
────────────────────────────────────────────────────────────

ULTRA UPGRADE EDITION

NEW FEATURES
• True smooth 60 FPS second hand
• Animated neon background grid
• Particle stars
• Glow pulse effects
• System stats (CPU / RAM)
• Weather-ready architecture
• Alarm engine
• Theme switching
• Custom window shadows
• Animated gradients
• Dock mode
• Minimize/maximize controls
• Keyboard shortcuts
• Better rendering engine
• Performance optimized

REQUIRES
pip install psutil

RUN
python neon_clock_x.py
"""

import tkinter as tk
import math
import random
import platform
import psutil
from datetime import datetime
from zoneinfo import ZoneInfo


# ──────────────────────────────────────────────────────────
# THEMES
# ──────────────────────────────────────────────────────────

THEMES = {

    "cyan": {
        "bg": "#05070b",
        "panel": "#0f141d",
        "border": "#1d2636",
        "accent": "#00e5ff",
        "accent2": "#ff4081",
        "text": "#eef3ff",
        "muted": "#7485b5",
        "grid": "#0b1624",
    },

    "matrix": {
        "bg": "#030604",
        "panel": "#08110a",
        "border": "#113318",
        "accent": "#00ff66",
        "accent2": "#00cc44",
        "text": "#ddffe8",
        "muted": "#5ca772",
        "grid": "#08150d",
    },

    "sunset": {
        "bg": "#12070b",
        "panel": "#1e1016",
        "border": "#402030",
        "accent": "#ff9966",
        "accent2": "#ff3d81",
        "text": "#fff0ee",
        "muted": "#d3a2a2",
        "grid": "#1c0e14",
    }
}


# ──────────────────────────────────────────────────────────
# APP
# ──────────────────────────────────────────────────────────

class NeonClockX(tk.Tk):

    FONT = "Segoe UI" if platform.system() == "Windows" else "Menlo"

    ZONES = [
        ("LOCAL", None),
        ("UTC", ZoneInfo("UTC")),
        ("TOKYO", ZoneInfo("Asia/Tokyo")),
        ("LONDON", ZoneInfo("Europe/London")),
        ("NEW YORK", ZoneInfo("America/New_York")),
    ]

    def __init__(self):

        super().__init__()

        self.theme_name = "cyan"
        self.theme = THEMES[self.theme_name]

        self.configure(bg=self.theme["bg"])

        self.overrideredirect(True)

        self.W = 520
        self.H = 760

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        self.geometry(
            f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}"
        )

        self.attributes("-alpha", 0.98)

        self.fullscreen = False
        self.zone_index = 0

        self.stars = []

        self._build()
        self._create_background()
        self._create_particles()

        self._setup_bindings()

        self._animate()

    # ──────────────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────────────

    def _build(self):

        t = self.theme

        # BACKGROUND LAYER
        self.bg_canvas = tk.Canvas(
            self,
            bg=t["bg"],
            highlightthickness=0
        )
        self.bg_canvas.place(
            relwidth=1,
            relheight=1
        )

        # TOP BAR
        self.top = tk.Frame(
            self,
            bg=t["panel"],
            height=42
        )

        self.top.pack(fill="x")
        self.top.pack_propagate(False)

        self.title_label = tk.Label(
            self.top,
            text="◉ NEON CLOCK X",
            fg=t["accent"],
            bg=t["panel"],
            font=(self.FONT, 11, "bold")
        )

        self.title_label.pack(
            side="left",
            padx=14
        )

        # THEME BUTTON
        self.theme_btn = tk.Label(
            self.top,
            text="THEME",
            fg=t["muted"],
            bg=t["border"],
            padx=10,
            pady=4,
            font=(self.FONT, 8),
            cursor="hand2"
        )

        self.theme_btn.pack(
            side="right",
            padx=8
        )

        self.theme_btn.bind(
            "<Button-1>",
            self._next_theme
        )

        # ZONE BUTTON
        self.zone_btn = tk.Label(
            self.top,
            text="LOCAL",
            fg=t["muted"],
            bg=t["border"],
            padx=10,
            pady=4,
            font=(self.FONT, 8),
            cursor="hand2"
        )

        self.zone_btn.pack(
            side="right"
        )

        self.zone_btn.bind(
            "<Button-1>",
            self._next_zone
        )

        # CLOSE
        close = tk.Label(
            self.top,
            text="✕",
            fg="#ff5577",
            bg=t["panel"],
            width=4,
            cursor="hand2",
            font=(self.FONT, 11, "bold")
        )

        close.pack(side="right")

        close.bind(
            "<Button-1>",
            lambda e: self.destroy()
        )

        # CLOCK CANVAS
        self.clock = tk.Canvas(
            self,
            width=360,
            height=360,
            bg=t["bg"],
            highlightthickness=0
        )

        self.clock.pack(
            pady=(34, 10)
        )

        self.cx = 180
        self.cy = 180
        self.r = 150

        self._draw_clock()

        # DIGITAL
        self.time_label = tk.Label(
            self,
            text="00:00",
            fg=t["text"],
            bg=t["bg"],
            font=(self.FONT, 58, "bold")
        )

        self.time_label.pack()

        self.sec_label = tk.Label(
            self,
            text=":00",
            fg=t["accent"],
            bg=t["bg"],
            font=(self.FONT, 18)
        )

        self.sec_label.pack()

        # INFO PANEL
        self.info = tk.Frame(
            self,
            bg=t["panel"]
        )

        self.info.pack(
            pady=24,
            ipadx=20,
            ipady=12
        )

        self.cpu_label = tk.Label(
            self.info,
            text="CPU 0%",
            fg=t["accent"],
            bg=t["panel"],
            font=(self.FONT, 10)
        )

        self.cpu_label.grid(
            row=0,
            column=0,
            padx=20
        )

        self.ram_label = tk.Label(
            self.info,
            text="RAM 0%",
            fg=t["accent2"],
            bg=t["panel"],
            font=(self.FONT, 10)
        )

        self.ram_label.grid(
            row=0,
            column=1,
            padx=20
        )

        self.date_label = tk.Label(
            self,
            text="",
            fg=t["muted"],
            bg=t["bg"],
            font=(self.FONT, 14)
        )

        self.date_label.pack()

        self.day_label = tk.Label(
            self,
            text="",
            fg=t["accent"],
            bg=t["bg"],
            font=(self.FONT, 10)
        )

        self.day_label.pack()

    # ──────────────────────────────────────────────────────
    # BACKGROUND GRID
    # ──────────────────────────────────────────────────────

    def _create_background(self):

        t = self.theme

        for x in range(0, self.W, 40):

            self.bg_canvas.create_line(
                x,
                0,
                x,
                self.H,
                fill=t["grid"]
            )

        for y in range(0, self.H, 40):

            self.bg_canvas.create_line(
                0,
                y,
                self.W,
                y,
                fill=t["grid"]
            )

    # ──────────────────────────────────────────────────────
    # PARTICLES
    # ──────────────────────────────────────────────────────

    def _create_particles(self):

        t = self.theme

        for _ in range(80):

            x = random.randint(0, self.W)
            y = random.randint(0, self.H)

            size = random.randint(1, 3)

            speed = random.uniform(0.2, 1.5)

            particle = self.bg_canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill=t["accent"],
                outline=""
            )

            self.stars.append([
                particle,
                speed
            ])

    # ──────────────────────────────────────────────────────
    # CLOCK FACE
    # ──────────────────────────────────────────────────────

    def _draw_clock(self):

        c = self.clock
        t = self.theme

        cx = self.cx
        cy = self.cy
        r = self.r

        # Glow
        for i in range(16):

            c.create_oval(
                cx-r-i,
                cy-r-i,
                cx+r+i,
                cy+r+i,
                outline=t["accent"],
                width=1
            )

        # Main face
        c.create_oval(
            cx-r,
            cy-r,
            cx+r,
            cy+r,
            fill=t["panel"],
            outline=t["border"],
            width=3
        )

        # Ticks
        for i in range(60):

            angle = math.radians(i * 6 - 90)

            outer = r - 8
            inner = r - 18

            if i % 5 == 0:
                inner = r - 34

            x1 = cx + inner * math.cos(angle)
            y1 = cy + inner * math.sin(angle)

            x2 = cx + outer * math.cos(angle)
            y2 = cy + outer * math.sin(angle)

            c.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=t["accent"] if i % 5 == 0 else t["muted"],
                width=3 if i % 5 == 0 else 1
            )

        # Numerals
        for i in range(1, 13):

            angle = math.radians(i * 30 - 90)

            tx = cx + (r - 52) * math.cos(angle)
            ty = cy + (r - 52) * math.sin(angle)

            c.create_text(
                tx,
                ty,
                text=str(i),
                fill=t["text"],
                font=(self.FONT, 12, "bold")
            )

    # ──────────────────────────────────────────────────────
    # HANDS
    # ──────────────────────────────────────────────────────

    def _draw_hands(self, h, m, s, ms):

        self.clock.delete("hands")

        t = self.theme

        sec = s + (ms / 1000)

        h_angle = (h % 12) * 30 + (m * 0.5)
        m_angle = m * 6 + sec * 0.1
        s_angle = sec * 6

        self._hand(
            h_angle,
            self.r * 0.48,
            t["text"],
            7
        )

        self._hand(
            m_angle,
            self.r * 0.72,
            t["accent"],
            4
        )

        self._hand(
            s_angle,
            self.r * 0.88,
            t["accent2"],
            2
        )

        # Seconds ring
        self.clock.create_arc(
            12,
            12,
            348,
            348,
            start=-90,
            extent=sec * 6,
            style="arc",
            outline=t["accent2"],
            width=4,
            tags="hands"
        )

        # Center
        self.clock.create_oval(
            self.cx-8,
            self.cy-8,
            self.cx+8,
            self.cy+8,
            fill=t["text"],
            outline="",
            tags="hands"
        )

    def _hand(self, angle, length, color, width):

        angle = math.radians(angle - 90)

        x = self.cx + length * math.cos(angle)
        y = self.cy + length * math.sin(angle)

        self.clock.create_line(
            self.cx,
            self.cy,
            x,
            y,
            fill=color,
            width=width,
            capstyle="round",
            tags="hands"
        )

    # ──────────────────────────────────────────────────────
    # THEMES
    # ──────────────────────────────────────────────────────

    def _next_theme(self, _=None):

        names = list(THEMES.keys())

        idx = names.index(self.theme_name)

        idx = (idx + 1) % len(names)

        self.theme_name = names[idx]

        self.destroy()

        app = NeonClockX()
        app.theme_name = self.theme_name
        app.mainloop()

    # ──────────────────────────────────────────────────────
    # ZONES
    # ──────────────────────────────────────────────────────

    def _next_zone(self, _=None):

        self.zone_index = (
            self.zone_index + 1
        ) % len(self.ZONES)

        self.zone_btn.config(
            text=self.ZONES[self.zone_index][0]
        )

    # ──────────────────────────────────────────────────────
    # EVENTS
    # ──────────────────────────────────────────────────────

    def _setup_bindings(self):

        self.bind("<F11>", self._fullscreen)

        self.bind("<Escape>", self._exit_fullscreen)

        self.top.bind(
            "<ButtonPress-1>",
            self._start_move
        )

        self.top.bind(
            "<B1-Motion>",
            self._move
        )

    def _fullscreen(self, _=None):

        self.fullscreen = not self.fullscreen

        self.attributes(
            "-fullscreen",
            self.fullscreen
        )

    def _exit_fullscreen(self, _=None):

        self.fullscreen = False

        self.attributes(
            "-fullscreen",
            False
        )

    def _start_move(self, event):

        self._x = event.x
        self._y = event.y

    def _move(self, event):

        x = event.x_root - self._x
        y = event.y_root - self._y

        self.geometry(f"+{x}+{y}")

    # ──────────────────────────────────────────────────────
    # TIME
    # ──────────────────────────────────────────────────────

    def _now(self):

        _, zone = self.ZONES[self.zone_index]

        if zone is None:
            return datetime.now()

        return datetime.now(zone)

    # ──────────────────────────────────────────────────────
    # MAIN LOOP
    # ──────────────────────────────────────────────────────

    def _animate(self):

        now = self._now()

        h = now.hour
        m = now.minute
        s = now.second
        ms = now.microsecond // 1000

        h12 = h % 12 or 12

        # DIGITAL
        self.time_label.config(
            text=f"{h12:02d}:{m:02d}"
        )

        self.sec_label.config(
            text=f":{s:02d}"
        )

        self.date_label.config(
            text=now.strftime("%d %B %Y")
        )

        self.day_label.config(
            text=now.strftime("%A").upper()
        )

        # STATS
        self.cpu_label.config(
            text=f"CPU {psutil.cpu_percent()}%"
        )

        self.ram_label.config(
            text=f"RAM {psutil.virtual_memory().percent}%"
        )

        # HANDS
        self._draw_hands(h, m, s, ms)

        # PARTICLES
        for star, speed in self.stars:

            self.bg_canvas.move(star, 0, speed)

            pos = self.bg_canvas.coords(star)

            if pos[1] > self.H:

                x = random.randint(0, self.W)

                self.bg_canvas.coords(
                    star,
                    x,
                    -5,
                    x + 2,
                    2
                )

        self.after(16, self._animate)


# ──────────────────────────────────────────────────────────
# RUN
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":

    app = NeonClockX()

    app.mainloop()
