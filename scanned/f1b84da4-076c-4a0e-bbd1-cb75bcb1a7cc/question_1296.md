# Q1296: Error propagation in make_signature downgrades a hard failure (plans/enroll_user.rs)

## Question
Can an unprivileged attacker force an error inside `make_signature` in [src/plans/enroll_user.rs](src/plans/enroll_user.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/plans/enroll_user.rs](src/plans/enroll_user.rs) -> `make_signature` (function)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `make_signature` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `make_signature` and asserting abort.
