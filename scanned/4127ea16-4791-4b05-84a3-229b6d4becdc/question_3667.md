# Q3667: Error propagation in Plan downgrades a hard failure (health_check/mod.rs)

## Question
Can an unprivileged attacker force an error inside `Plan` in [src/plans/health_check/mod.rs](src/plans/health_check/mod.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/plans/health_check/mod.rs](src/plans/health_check/mod.rs) -> `Plan` (type)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `Plan` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `Plan` and asserting abort.
