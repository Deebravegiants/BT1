# Q3928: freeze_collection can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `freeze_collection` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: substrate/frame/uniques/src/lib.rs::freeze_collection
- Entrypoint: signed extrinsic `freeze_collection`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: Permanent asset lock or state corruption that blocks transfers
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
