# ADR-001: Windowed Time Clock — Architecture Decision Record

| Field       | Value                          |
|-------------|--------------------------------|
| **Status**  | ✅ Accepted                    |
| **Date**    | 2026-05-18                     |
| **Author**  | —                              |
| **Deciders**| —                              |

---

## Context

A lightweight desktop time clock was needed that:

- Displays the **current local time** (digital + analog) in a persistent window
- Requires **zero installation** beyond a standard Python environment
- Runs cross-platform (Windows, macOS, Linux)
- Is self-contained in a single file with no external dependencies

Several approaches were considered: a web-based clock (HTML/JS served locally), a system-tray widget, a full GUI framework app (PyQt / wxPython), and a pure-`tkinter` window.

---

## Decision

We chose **Python + tkinter** as the sole technology stack, delivered as a single `.py` script.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **tkinter** ✅ | Stdlib — zero deps; cross-platform; lightweight | Limited styling vs. native toolkits |
| PyQt6 / PySide6 | Rich widget set, native look | ~50 MB install; not stdlib |
| wxPython | Native OS widgets | Heavier install; less Pythonic API |
| HTML + `http.server` | CSS/JS flexibility | Requires browser; no true "window" |
| System tray (`pystray`) | Minimal screen footprint | Extra dependency; less visible |

### Why tkinter

1. **Zero dependencies** — ships with CPython on all major platforms; `pip install` nothing.
2. **Single-file distribution** — the entire app is one `.py` file, trivial to share or audit.
3. **Canvas drawing API** — `tk.Canvas` is expressive enough to render a smooth analog clock face with custom tick marks, hands, and glow rings without any image assets.
4. **Cross-platform** — identical behaviour on Windows, macOS, and Linux without conditional code paths.
5. **Low resource usage** — idle CPU ≈ 0%; memory footprint < 20 MB.

---

## Implementation Details

### Clock update strategy

The tick loop uses **millisecond-aligned scheduling** rather than a fixed 1 000 ms interval:

```python
ms = now.microsecond // 1000
self.after(1000 - ms, self._tick)
```

This keeps the second hand in sync with the wall clock even if frames are occasionally delayed, avoiding drift accumulation over long runtimes.

### Analog rendering

All clock geometry is drawn imperatively on a `tk.Canvas` each tick:

- Static elements (face, ticks, numerals) are drawn once at startup.
- Hand elements are tagged `"hand"` and deleted/redrawn every second via `canvas.delete("hand")`.
- A shadow line is drawn before each hand (offset by 1 px) to simulate depth without image assets.

### UTC toggle

A `_tz_utc` boolean flag switches between `datetime.now()` and `datetime.utcnow()`. This is intentionally simple — full IANA timezone support (e.g. via `zoneinfo`) was out of scope and would add complexity without benefiting the primary use case.

### Font selection

`Courier New` is used on Windows, `Menlo` on macOS/Linux. Both are monospaced system fonts that render the digital readout without character-width jitter as digits change.

---

## Consequences

### Positive

- No `pip install` step; works out of the box on any standard Python 3.x install.
- Entire codebase is one file (~230 lines); easy to read, fork, or embed.
- Millisecond-aligned tick eliminates long-running drift.

### Negative / Trade-offs

- `tkinter` styling is limited compared to Qt or a browser-based UI — custom theming requires manual Canvas drawing.
- `datetime.utcnow()` is deprecated in Python 3.12+ in favour of `datetime.now(timezone.utc)`; a future patch should migrate to the aware-datetime API.
- No true multi-timezone support — only LOCAL and UTC are offered.

### Future Considerations

| ID | Improvement |
|----|-------------|
| F-01 | Migrate `utcnow()` → `datetime.now(timezone.utc)` for Python 3.12+ compatibility |
| F-02 | Add IANA timezone selector via `zoneinfo` (stdlib since 3.9) |
| F-03 | Add a stopwatch / countdown timer panel |
| F-04 | Persist window position between sessions using a small JSON config file |
| F-05 | Package as a standalone executable with `PyInstaller` for non-Python users |

---

## References

- [tkinter documentation](https://docs.python.org/3/library/tkinter.html)
- [Python `datetime` module](https://docs.python.org/3/library/datetime.html)
- [PEP 615 — `zoneinfo` standard library](https://peps.python.org/pep-0615/)
- [ADR template by Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
