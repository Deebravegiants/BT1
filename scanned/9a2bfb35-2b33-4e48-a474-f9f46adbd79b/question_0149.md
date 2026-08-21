# Q0149: Error propagation in Plan downgrades a hard failure (plans/detect_face.rs)

## Question
Can an unprivileged attacker force an error inside `Plan` in [src/plans/detect_face.rs](src/plans/detect_face.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/plans/detect_face.rs](src/plans/detect_face.rs) -> `Plan` (type)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `Plan` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `Plan` and asserting abort.
