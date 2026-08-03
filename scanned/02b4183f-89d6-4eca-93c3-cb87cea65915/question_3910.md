# Q3910: set_accept_ownership can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `set_accept_ownership` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::set_accept_ownership
- Entrypoint: signed extrinsic `set_accept_ownership`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: Permanent asset lock or state corruption that blocks transfers
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
