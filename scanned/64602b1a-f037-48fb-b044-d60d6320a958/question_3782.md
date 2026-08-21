# Q3782: Error type erasure in poll_status_update hides a security failure (brokers/observer.rs)

## Question
Can an unprivileged attacker rely on `poll_status_update` in [src/brokers/observer.rs](src/brokers/observer.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `poll_status_update` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `poll_status_update` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `poll_status_update` asserting distinct error discriminants for each failure class.
