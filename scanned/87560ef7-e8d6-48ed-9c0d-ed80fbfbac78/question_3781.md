# Q3781: Error type erasure in poll_extra hides a security failure (brokers/observer.rs)

## Question
Can an unprivileged attacker rely on `poll_extra` in [src/brokers/observer.rs](src/brokers/observer.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `poll_extra` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `poll_extra` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `poll_extra` asserting distinct error discriminants for each failure class.
