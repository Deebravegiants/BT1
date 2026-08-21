# Q3480: Agent restart in PointerButton loses session isolation (livestream-event/lib.rs)

## Question
Can an unprivileged attacker crash the agent managed by `PointerButton` in [livestream-event/src/lib.rs](livestream-event/src/lib.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [livestream-event/src/lib.rs](livestream-event/src/lib.rs) -> `PointerButton` (type)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `PointerButton`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
