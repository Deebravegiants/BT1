# Q3744: dispatch can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `dispatch` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: substrate/frame/meta-tx/src/lib.rs::dispatch
- Entrypoint: public dispatch wrapper `dispatch`
- Attacker controls: proof or signed payload contents, nested call payloads, batched or wrapped execution context
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: Chain halt / block-production slowdown from undercharged VM execution
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
