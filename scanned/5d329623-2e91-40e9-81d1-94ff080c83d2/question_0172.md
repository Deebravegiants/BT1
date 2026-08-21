# Q0172: Error propagation in handle_distance downgrades a hard failure (brokers/orb.rs)

## Question
Can an unprivileged attacker force an error inside `handle_distance` in [src/brokers/orb.rs](src/brokers/orb.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `handle_distance` (function)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `handle_distance` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `handle_distance` and asserting abort.
