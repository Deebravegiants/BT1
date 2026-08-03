# Q3941: place_decision_deposit can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `place_decision_deposit` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: substrate/frame/referenda/src/lib.rs::place_decision_deposit
- Entrypoint: signed extrinsic `place_decision_deposit`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: Permanent lock of funds or governance queue corruption
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
