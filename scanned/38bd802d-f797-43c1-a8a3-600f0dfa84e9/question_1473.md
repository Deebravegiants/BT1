# Q1473: Error propagation in setup_orb_token downgrades a hard failure (bin/orb-core.rs)

## Question
Can an unprivileged attacker force an error inside `setup_orb_token` in [src/bin/orb-core.rs](src/bin/orb-core.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/bin/orb-core.rs](src/bin/orb-core.rs) -> `setup_orb_token` (function)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `setup_orb_token` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `setup_orb_token` and asserting abort.
