# Q3655: Error propagation in ir_net_warmup downgrades a hard failure (plans/warmup.rs)

## Question
Can an unprivileged attacker force an error inside `ir_net_warmup` in [src/plans/warmup.rs](src/plans/warmup.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/plans/warmup.rs](src/plans/warmup.rs) -> `ir_net_warmup` (function)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `ir_net_warmup` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `ir_net_warmup` and asserting abort.
