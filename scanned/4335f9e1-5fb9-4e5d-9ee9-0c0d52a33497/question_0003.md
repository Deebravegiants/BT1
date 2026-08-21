# Q0003: Timing/ordering race on the scan handoff through handle_rgb_camera (qr_scan/mod.rs)

## Question
Can an unprivileged attacker swap the presented code in the window between validation and use in `handle_rgb_camera` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs), so the value validated is not the value consumed (TOCTOU) by the downstream signup?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `handle_rgb_camera` (function)
- Entrypoint: Rapidly alternating two QR codes in front of the camera
- Attacker controls: which payload is visible at each frame boundary
- Exploit idea: Alternate a benign and a malicious payload to land the swap between the check and the consume in `handle_rgb_camera`.
- Invariant to test: The validated payload and the consumed payload are the same immutable value.
- Expected Immunefi impact: Signup proceeding on an unvalidated attacker payload
- Fast validation: Concurrency test interleaving two decodes and asserting validate/consume operate on one snapshot.
