# Q0286: Error propagation in log_mcu_motor_range downgrades a hard failure (brokers/observer.rs)

## Question
Can an unprivileged attacker force an error inside `log_mcu_motor_range` in [src/brokers/observer.rs](src/brokers/observer.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `log_mcu_motor_range` (function)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `log_mcu_motor_range` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `log_mcu_motor_range` and asserting abort.
