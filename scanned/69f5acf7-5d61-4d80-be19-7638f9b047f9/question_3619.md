# Q3619: Agent restart in is_orb_os_version_allowed loses session isolation (plans/mod.rs)

## Question
Can an unprivileged attacker crash the agent managed by `is_orb_os_version_allowed` in [src/plans/mod.rs](src/plans/mod.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `is_orb_os_version_allowed` (function)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `is_orb_os_version_allowed`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
