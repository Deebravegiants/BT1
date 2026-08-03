# Q3876: proxy can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `proxy` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::proxy
- Entrypoint: public dispatch wrapper `proxy`
- Attacker controls: nested call payloads, batched or wrapped execution context
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: State corruption or underpriced wrapped execution leading to chain degradation
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
