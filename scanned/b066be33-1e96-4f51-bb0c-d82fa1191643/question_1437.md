# Q1437: Agent restart in poll_extra loses session isolation (brokers/observer.rs)

## Question
Can an unprivileged attacker crash the agent managed by `poll_extra` in [src/brokers/observer.rs](src/brokers/observer.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `poll_extra` (function)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `poll_extra`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
