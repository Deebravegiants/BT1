# Q1375: Error type erasure in start_ir_auto_exposure hides a security failure (brokers/orb.rs)

## Question
Can an unprivileged attacker rely on `start_ir_auto_exposure` in [src/brokers/orb.rs](src/brokers/orb.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `start_ir_auto_exposure` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `start_ir_auto_exposure` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `start_ir_auto_exposure` asserting distinct error discriminants for each failure class.
