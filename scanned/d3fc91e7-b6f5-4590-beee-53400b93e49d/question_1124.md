# Q1124: Error type erasure in Event hides a security failure (livestream/upstream.rs)

## Question
Can an unprivileged attacker rely on `Event` in [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) -> `Event` (type)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `Event` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `Event` asserting distinct error discriminants for each failure class.
