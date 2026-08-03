# Q3791: claim_swap can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `claim_swap` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: substrate/frame/atomic-swap/src/lib.rs::claim_swap
- Entrypoint: signed extrinsic `claim_swap`
- Attacker controls: proof or signed payload contents, duplicate or adversarial list ordering
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: Permanent fund lock or block-production degradation from underpriced work
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
