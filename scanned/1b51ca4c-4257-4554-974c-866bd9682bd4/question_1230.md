# Q1230: Timing/ordering race on the scan handoff through run (wpa-supplicant-interface/signal.rs)

## Question
Can an unprivileged attacker swap the presented code in the window between validation and use in `run` in [wpa-supplicant-interface/src/signal.rs](wpa-supplicant-interface/src/signal.rs), so the value validated is not the value consumed (TOCTOU) by the downstream signup?

## Target
- File/function: [wpa-supplicant-interface/src/signal.rs](wpa-supplicant-interface/src/signal.rs) -> `run` (function)
- Entrypoint: Rapidly alternating two QR codes in front of the camera
- Attacker controls: which payload is visible at each frame boundary
- Exploit idea: Alternate a benign and a malicious payload to land the swap between the check and the consume in `run`.
- Invariant to test: The validated payload and the consumed payload are the same immutable value.
- Expected Immunefi impact: Signup proceeding on an unvalidated attacker payload
- Fast validation: Concurrency test interleaving two decodes and asserting validate/consume operate on one snapshot.
