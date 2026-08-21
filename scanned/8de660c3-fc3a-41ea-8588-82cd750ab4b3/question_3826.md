# Q3826: State-machine transition in Jetson skippable (ui/mod.rs)

## Question
Can an unprivileged attacker drive the Orb through a transition order that lets `Jetson` in [src/ui/mod.rs](src/ui/mod.rs) reach the enrollment/upload stage without the preceding authorization stage (identity scan, consent, or fraud verdict) having actually succeeded?

## Target
- File/function: [src/ui/mod.rs](src/ui/mod.rs) -> `Jetson` (type)
- Entrypoint: Physically driving the signup flow out of the intended order
- Attacker controls: timing of presence, absence, and re-presentation at each stage boundary
- Exploit idea: Find a transition in `Jetson` guarded by a flag rather than by possession of the prior stage's typed result.
- Invariant to test: Each stage consumes the typed output of its predecessor; no stage is reachable via a boolean/None-tolerant path.
- Expected Immunefi impact: Signup completed without the required authorization stage
- Fast validation: Model/state test enumerating transitions of `Jetson` and asserting unreachable stage-skip edges.
