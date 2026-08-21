# Q2248: Agent restart in sem_wait loses session isolation (agentwire/port.rs)

## Question
Can an unprivileged attacker crash the agent managed by `sem_wait` in [agentwire/src/port.rs](agentwire/src/port.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `sem_wait` (function)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `sem_wait`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
