# Q2567: Agent restart in send_rgb_net_face_identifier_input loses session isolation (brokers/orb.rs)

## Question
Can an unprivileged attacker crash the agent managed by `send_rgb_net_face_identifier_input` in [src/brokers/orb.rs](src/brokers/orb.rs) so the restarted instance is reused with state or buffers from the previous session still present or missing without the session being invalidated?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `send_rgb_net_face_identifier_input` (function)
- Entrypoint: Input that reliably crashes the agent
- Attacker controls: the crashing input and its timing
- Exploit idea: Check `send_rgb_net_face_identifier_input`'s restart policy for state reset and session invalidation.
- Invariant to test: Agent restart resets all state and invalidates any session that depended on it.
- Expected Immunefi impact: Cross-session data bleed or silently skipped checks after a restart
- Fast validation: Fault-injection test crashing the agent mid-session and asserting reset plus abort.
