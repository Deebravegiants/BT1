# Q3748: Session identifier generation in init_qr_code (brokers/orb.rs)

## Question
Can an unprivileged attacker predict, collide with, or influence the session/signup identifier produced or consumed by `init_qr_code` in [src/brokers/orb.rs](src/brokers/orb.rs), so their capture is filed under an identifier that another signup also uses?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `init_qr_code` (function)
- Entrypoint: Observing and timing their own signups to infer identifier construction
- Attacker controls: timing and any attacker-supplied component of the identifier
- Exploit idea: Check `init_qr_code` for identifiers derived from time, counters, or attacker input rather than a CSPRNG.
- Invariant to test: Signup identifiers are unpredictable, unique, and not attacker-influenced.
- Expected Immunefi impact: Collision or predictability enabling misattribution of biometric records
- Fast validation: Statistical test on identifier generation asserting entropy and no attacker-controlled component.
