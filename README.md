# FM-1 Pocket

A playable M-VAVE FM-1 for the phone. It runs the official **FM1 Open V14** firmware, compiled to WebAssembly, behind a custom faceplate. Add it to the iPhone home screen from Safari (Share → Add to Home Screen); after the first open it works offline.

## Source and license

- Firmware: [m-vave/fm1_open](https://github.com/m-vave/fm1_open) at commit `4c7496d`, unmodified. `build/simulator.wasm` is compiled from `app/` (excluding `app/board/`), `web/` and `third_party/synth/` with WASI SDK 27, using the flags in that repo's `tools/Build-Web.ps1`.
- The engine runtime in the page is adapted from that repo's `sdk/Simulator.js`.
- License: GPL-3.0-only with the FM1 SDK linking exception, as in the FM1 Open repository. See its `LICENSE.md` and `THIRD_PARTY.md`.

Have Fun :)
