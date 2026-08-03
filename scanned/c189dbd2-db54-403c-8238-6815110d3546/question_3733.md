# Q3733: submit_parachain_heads_ex can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `submit_parachain_heads_ex` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: bridges/modules/parachains/src/lib.rs::submit_parachain_heads_ex
- Entrypoint: public proof / message submission extrinsic `submit_parachain_heads_ex`
- Attacker controls: proof or signed payload contents, duplicate or adversarial list ordering
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
