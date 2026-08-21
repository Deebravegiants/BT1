# Q0060: main state not cleared between scans (orb-backend-connect/main.rs)

## Question
Can an unprivileged attacker exploit `main` in [orb-backend-connect/src/main.rs](orb-backend-connect/src/main.rs) retaining decoded state from a previous scan, so a subsequent user's session inherits the attacker's parsed identity, mode, or network selection?

## Target
- File/function: [orb-backend-connect/src/main.rs](orb-backend-connect/src/main.rs) -> `main` (function)
- Entrypoint: Sequence of scans across two sessions on the same Orb
- Attacker controls: ordering and timing of their own scan relative to the victim's
- Exploit idea: Scan, abort, then let the next session start and check whether `main`'s cached/last-decoded value is reused.
- Invariant to test: Decoded scan state is scoped to one session and cleared on abort, timeout, and completion.
- Expected Immunefi impact: Cross-session identity bleed binding a victim's capture to the attacker's identity
- Fast validation: Integration test asserting the decode cache is empty at session start.
