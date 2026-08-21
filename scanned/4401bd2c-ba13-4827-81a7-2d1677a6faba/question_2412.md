# Q2412: Session identifier generation in biometric_input (plans/mod.rs)

## Question
Can an unprivileged attacker predict, collide with, or influence the session/signup identifier produced or consumed by `biometric_input` in [src/plans/mod.rs](src/plans/mod.rs), so their capture is filed under an identifier that another signup also uses?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `biometric_input` (function)
- Entrypoint: Observing and timing their own signups to infer identifier construction
- Attacker controls: timing and any attacker-supplied component of the identifier
- Exploit idea: Check `biometric_input` for identifiers derived from time, counters, or attacker input rather than a CSPRNG.
- Invariant to test: Signup identifiers are unpredictable, unique, and not attacker-influenced.
- Expected Immunefi impact: Collision or predictability enabling misattribution of biometric records
- Fast validation: Statistical test on identifier generation asserting entropy and no attacker-controlled component.
