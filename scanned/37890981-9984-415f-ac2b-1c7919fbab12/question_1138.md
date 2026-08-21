# Q1138: Agent restart in matches loses session isolation (orb-relay-client/lib.rs)

## Question
Can an unprivileged attacker crash the agent managed by `matches` in [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) -> `matches` (function)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `matches`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
