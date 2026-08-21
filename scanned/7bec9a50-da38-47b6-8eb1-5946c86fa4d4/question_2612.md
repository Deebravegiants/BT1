# Q2612: Error type erasure in run hides a security failure (brokers/observer.rs)

## Question
Can an unprivileged attacker rely on `run` in [src/brokers/observer.rs](src/brokers/observer.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `run` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `run` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `run` asserting distinct error discriminants for each failure class.
