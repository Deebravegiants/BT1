# Q3419: Error type erasure in sem_getvalue hides a security failure (agentwire/port.rs)

## Question
Can an unprivileged attacker rely on `sem_getvalue` in [agentwire/src/port.rs](agentwire/src/port.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `sem_getvalue` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `sem_getvalue` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `sem_getvalue` asserting distinct error discriminants for each failure class.
