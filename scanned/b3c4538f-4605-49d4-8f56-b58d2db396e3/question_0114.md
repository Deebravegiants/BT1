# Q0114: State-machine transition in proceed_with_biometric_capture skippable (plans/mod.rs)

## Question
Can an unprivileged attacker drive the Orb through a transition order that lets `proceed_with_biometric_capture` in [src/plans/mod.rs](src/plans/mod.rs) reach the enrollment/upload stage without the preceding authorization stage (identity scan, consent, or fraud verdict) having actually succeeded?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `proceed_with_biometric_capture` (function)
- Entrypoint: Physically driving the signup flow out of the intended order
- Attacker controls: timing of presence, absence, and re-presentation at each stage boundary
- Exploit idea: Find a transition in `proceed_with_biometric_capture` guarded by a flag rather than by possession of the prior stage's typed result.
- Invariant to test: Each stage consumes the typed output of its predecessor; no stage is reachable via a boolean/None-tolerant path.
- Expected Immunefi impact: Signup completed without the required authorization stage
- Fast validation: Model/state test enumerating transitions of `proceed_with_biometric_capture` and asserting unreachable stage-skip edges.
