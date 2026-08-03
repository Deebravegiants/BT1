# Q3870: note_preimage can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `note_preimage` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: substrate/frame/preimage/src/lib.rs::note_preimage
- Entrypoint: signed extrinsic `note_preimage`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: State corruption or underpriced wrapped execution leading to chain degradation
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
