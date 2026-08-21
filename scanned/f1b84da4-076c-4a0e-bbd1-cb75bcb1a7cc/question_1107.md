# Q1107: Agent restart in spawn_task loses session isolation (agent/task.rs)

## Question
Can an unprivileged attacker crash the agent managed by `spawn_task` in [agentwire/src/agent/task.rs](agentwire/src/agent/task.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [agentwire/src/agent/task.rs](agentwire/src/agent/task.rs) -> `spawn_task` (function)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `spawn_task`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
