# Q0221: Error propagation in send_ir_net_estimate downgrades a hard failure (brokers/orb.rs)

## Question
Can an unprivileged attacker force an error inside `send_ir_net_estimate` in [src/brokers/orb.rs](src/brokers/orb.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `send_ir_net_estimate` (function)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `send_ir_net_estimate` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `send_ir_net_estimate` and asserting abort.
