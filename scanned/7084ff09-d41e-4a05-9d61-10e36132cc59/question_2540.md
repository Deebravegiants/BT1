# Q2540: Agent restart in reset_rgb_camera loses session isolation (brokers/orb.rs)

## Question
Can an unprivileged attacker crash the agent managed by `reset_rgb_camera` in [src/brokers/orb.rs](src/brokers/orb.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `reset_rgb_camera` (function)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `reset_rgb_camera`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
