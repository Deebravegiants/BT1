# Q0311: Session identifier generation in Fake (ui/mod.rs)

## Question
Can an unprivileged attacker predict, collide with, or influence the session/signup identifier produced or consumed by `Fake` in [src/ui/mod.rs](src/ui/mod.rs), so their capture is filed under an identifier that another signup also uses?

## Target
- File/function: [src/ui/mod.rs](src/ui/mod.rs) -> `Fake` (type)
- Entrypoint: Observing and timing their own signups to infer identifier construction
- Attacker controls: timing and any attacker-supplied component of the identifier
- Exploit idea: Check `Fake` for identifiers derived from time, counters, or attacker input rather than a CSPRNG.
- Invariant to test: Signup identifiers are unpredictable, unique, and not attacker-influenced.
- Expected Immunefi impact: Collision or predictability enabling misattribution of biometric records
- Fast validation: Statistical test on identifier generation asserting entropy and no attacker-controlled component.
