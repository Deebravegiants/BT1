# Q2263: Agent restart in Cell loses session isolation (agent/mod.rs)

## Question
Can an unprivileged attacker crash the agent managed by `Cell` in [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) -> `Cell` (type)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `Cell`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
