# Q2318: Session identifier generation in new_as_app_zkp (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker predict, collide with, or influence the session/signup identifier produced or consumed by `new_as_app_zkp` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs), so their capture is filed under an identifier that another signup also uses?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `new_as_app_zkp` (function)
- Entrypoint: Observing and timing their own signups to infer identifier construction
- Attacker controls: timing and any attacker-supplied component of the identifier
- Exploit idea: Check `new_as_app_zkp` for identifiers derived from time, counters, or attacker input rather than a CSPRNG.
- Invariant to test: Signup identifiers are unpredictable, unique, and not attacker-influenced.
- Expected Immunefi impact: Collision or predictability enabling misattribution of biometric records
- Fast validation: Statistical test on identifier generation asserting entropy and no attacker-controlled component.
