# Q2394: Opt state not cleared between scans (wpa-supplicant-interface/main.rs)

## Question
Can an unprivileged attacker exploit `Opt` in [wpa-supplicant-interface/src/main.rs](wpa-supplicant-interface/src/main.rs) retaining decoded state from a previous scan, so a subsequent user's session inherits the attacker's parsed identity, mode, or network selection?

## Target
- File/function: [wpa-supplicant-interface/src/main.rs](wpa-supplicant-interface/src/main.rs) -> `Opt` (type)
- Entrypoint: Sequence of scans across two sessions on the same Orb
- Attacker controls: ordering and timing of their own scan relative to the victim's
- Exploit idea: Scan, abort, then let the next session start and check whether `Opt`'s cached/last-decoded value is reused.
- Invariant to test: Decoded scan state is scoped to one session and cleared on abort, timeout, and completion.
- Expected Immunefi impact: Cross-session identity bleed binding a victim's capture to the attacker's identity
- Fast validation: Integration test asserting the decode cache is empty at session start.
