"""
Windowed Time Clock — a sleek, dark-themed desktop clock built with tkinter.
Features: digital clock, date display, analog clock face, timezone toggle.
Run with: python time_clock.py
"""

import tkinter as tk
import time
import math
from datetime import datetime
import platform


# ── Palette ──────────────────────────────────────────────────────────────────
BG          = "#0d0d0f"
PANEL       = "#14141a"
BORDER      = "#1e1e2a"
ACCENT      = "#00e5ff"
ACCENT2     = "#ff4081"
TEXT_MAIN   = "#e8e8f0"
TEXT_DIM    = "#4a4a60"
TEXT_MID    = "#8888a8"
TICK_HOUR   = "#00e5ff"
TICK_MIN    = "#00b4cc"
HAND_HOUR   = "#e8e8f0"
HAND_MIN    = "#00e5ff"
HAND_SEC    = "#ff4081"
HAND_CENTER = "#ffffff"


class TimeClock(tk.Tk):
    FONT_FAMILY = "Courier New" if platform.system() == "Windows" else "Menlo"

    def __init__(self):
        super().__init__()
        self.title("Time Clock")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Center on screen
        w, h = 400, 560
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        # Remove default title bar on macOS for cleaner look (optional)
        self._build_ui()
        self._tick()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top bar ──
        top = tk.Frame(self, bg=PANEL, height=44)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(
            top, text="◉  TIME CLOCK", bg=PANEL,
            fg=ACCENT, font=(self.FONT_FAMILY, 11, "bold"),
            anchor="w", padx=16
        ).pack(side="left", fill="y")

        self._tz_var = tk.StringVar(value="LOCAL")
        tz_btn = tk.Button(
            top, textvariable=self._tz_var, bg=BORDER, fg=TEXT_MID,
            font=(self.FONT_FAMILY, 9), bd=0, relief="flat",
            activebackground=ACCENT, activeforeground=BG,
            padx=10, pady=4, cursor="hand2",
            command=self._toggle_tz
        )
        tz_btn.pack(side="right", padx=12, pady=8)

        # ── Divider ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ── Analog clock ──
        self._canvas = tk.Canvas(
            self, width=260, height=260,
            bg=BG, highlightthickness=0
        )
        self._canvas.pack(pady=(28, 10))
        self._draw_clock_base()

        # ── Digital time ──
        self._time_label = tk.Label(
            self, text="", bg=BG, fg=TEXT_MAIN,
            font=(self.FONT_FAMILY, 44, "bold")
        )
        self._time_label.pack()

        # ── Seconds bar ──
        sec_frame = tk.Frame(self, bg=BG)
        sec_frame.pack(pady=(4, 0))
        self._sec_label = tk.Label(
            sec_frame, text="", bg=BG, fg=ACCENT,
            font=(self.FONT_FAMILY, 13)
        )
        self._sec_label.pack(side="left")

        # ── AM/PM badge ──
        self._ampm_label = tk.Label(
            self, text="", bg=PANEL, fg=ACCENT2,
            font=(self.FONT_FAMILY, 12, "bold"),
            width=4, pady=2
        )
        self._ampm_label.pack(pady=(4, 0))

        # ── Divider ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", pady=(16, 0))

        # ── Date bar ──
        self._date_label = tk.Label(
            self, text="", bg=BG, fg=TEXT_MID,
            font=(self.FONT_FAMILY, 13)
        )
        self._date_label.pack(pady=(12, 0))

        # ── Day of week ──
        self._day_label = tk.Label(
            self, text="", bg=BG, fg=TEXT_DIM,
            font=(self.FONT_FAMILY, 10)
        )
        self._day_label.pack(pady=(2, 16))

        # ── Bottom accent line ──
        accent_bar = tk.Canvas(self, width=400, height=3, bg=BG, highlightthickness=0)
        accent_bar.pack(fill="x", side="bottom")
        accent_bar.create_line(0, 1, 400, 1, fill=ACCENT, width=2)
        accent_bar.create_line(200, 1, 400, 1, fill=ACCENT2, width=2)

    # ── Clock face (static elements) ─────────────────────────────────────────

    def _draw_clock_base(self):
        cx, cy, r = 130, 130, 115
        c = self._canvas

        # Outer glow ring
        for i in range(4, 0, -1):
            shade = int(0x1e * (i / 4))
            col = f"#{shade:02x}{shade:02x}{shade + 0x10:02x}"
            c.create_oval(
                cx - r - i, cy - r - i,
                cx + r + i, cy + r + i,
                outline=col, width=1
            )

        # Face
        c.create_oval(cx-r, cy-r, cx+r, cy+r, fill=PANEL, outline=BORDER, width=2)

        # Hour ticks
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = cx + (r - 6) * math.cos(angle)
            y1 = cy + (r - 6) * math.sin(angle)
            x2 = cx + (r - 20) * math.cos(angle)
            y2 = cy + (r - 20) * math.sin(angle)
            c.create_line(x1, y1, x2, y2, fill=TICK_HOUR, width=2, capstyle="round")

        # Minute ticks
        for i in range(60):
            if i % 5 == 0:
                continue
            angle = math.radians(i * 6 - 90)
            x1 = cx + (r - 6) * math.cos(angle)
            y1 = cy + (r - 6) * math.sin(angle)
            x2 = cx + (r - 13) * math.cos(angle)
            y2 = cy + (r - 13) * math.sin(angle)
            c.create_line(x1, y1, x2, y2, fill=TEXT_DIM, width=1)

        # Hour numerals
        for i in range(1, 13):
            angle = math.radians(i * 30 - 90)
            nx = cx + (r - 34) * math.cos(angle)
            ny = cy + (r - 34) * math.sin(angle)
            c.create_text(
                nx, ny, text=str(i),
                fill=TEXT_MID, font=(self.FONT_FAMILY, 8, "bold")
            )

        # Store center for hands
        self._cx, self._cy, self._r = cx, cy, r

    def _draw_hands(self, h, m, s):
        cx, cy, r = self._cx, self._cy, self._r
        c = self._canvas

        # Delete old hands
        c.delete("hand")

        def hand(angle_deg, length, color, width, tag="hand"):
            angle = math.radians(angle_deg - 90)
            x = cx + length * math.cos(angle)
            y = cy + length * math.sin(angle)
            # Shadow
            c.create_line(
                cx+1, cy+1, x+1, y+1,
                fill="#000000", width=width + 2,
                capstyle="round", tags=tag
            )
            c.create_line(
                cx, cy, x, y,
                fill=color, width=width,
                capstyle="round", tags=tag
            )

        # Hour hand (smooth)
        h_angle = (h % 12) * 30 + m * 0.5 + s * (0.5 / 60)
        hand(h_angle, r * 0.52, HAND_HOUR, 4)

        # Minute hand (smooth)
        m_angle = m * 6 + s * 0.1
        hand(m_angle, r * 0.78, HAND_MIN, 2)

        # Second hand
        s_angle = s * 6
        # Tail
        tail_angle = math.radians(s_angle - 90 + 180)
        tx = cx + (r * 0.20) * math.cos(tail_angle)
        ty = cy + (r * 0.20) * math.sin(tail_angle)
        c.create_line(cx, cy, tx, ty, fill=HAND_SEC, width=1, tags="hand")
        # Main
        angle = math.radians(s_angle - 90)
        sx = cx + (r * 0.88) * math.cos(angle)
        sy = cy + (r * 0.88) * math.sin(angle)
        c.create_line(cx, cy, sx, sy, fill=HAND_SEC, width=1, tags="hand")

        # Center dot
        c.create_oval(cx-5, cy-5, cx+5, cy+5, fill=HAND_CENTER, outline="", tags="hand")
        c.create_oval(cx-2, cy-2, cx+2, cy+2, fill=ACCENT2, outline="", tags="hand")

    # ── Timezone toggle ───────────────────────────────────────────────────────

    _tz_utc = False

    def _toggle_tz(self):
        self._tz_utc = not self._tz_utc
        self._tz_var.set("UTC" if self._tz_utc else "LOCAL")

    # ── Tick ─────────────────────────────────────────────────────────────────

    def _tick(self):
        now = datetime.utcnow() if self._tz_utc else datetime.now()

        h, m, s = now.hour, now.minute, now.second

        # Digital
        hour12 = h % 12 or 12
        ampm = "AM" if h < 12 else "PM"
        self._time_label.config(text=f"{hour12:02d}:{m:02d}")
        self._sec_label.config(text=f":{s:02d}")
        self._ampm_label.config(text=ampm)

        # Date
        self._date_label.config(
            text=now.strftime("%d %B %Y")
            + ("  ·  UTC" if self._tz_utc else "")
        )
        self._day_label.config(text=now.strftime("%A").upper())

        # Analog
        self._draw_hands(h, m, s)

        # Millisecond-aligned tick for smoothness
        ms = now.microsecond // 1000
        self.after(1000 - ms, self._tick)


if __name__ == "__main__":
    app = TimeClock()
    app.mainloop()
