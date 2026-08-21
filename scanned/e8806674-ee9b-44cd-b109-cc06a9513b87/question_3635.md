# Q3635: Error propagation in QrCodes downgrades a hard failure (plans/mod.rs)

## Question
Can an unprivileged attacker force an error inside `QrCodes` in [src/plans/mod.rs](src/plans/mod.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `QrCodes` (type)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `QrCodes` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `QrCodes` and asserting abort.
