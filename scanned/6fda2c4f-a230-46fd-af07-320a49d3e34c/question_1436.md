# Q1436: Agent restart in handle_gps loses session isolation (brokers/observer.rs)

## Question
Can an unprivileged attacker crash the agent managed by `handle_gps` in [src/brokers/observer.rs](src/brokers/observer.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `handle_gps` (function)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `handle_gps`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
