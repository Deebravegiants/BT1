# Q2291: Error type erasure in Input hides a security failure (livestream/mod.rs)

## Question
Can an unprivileged attacker rely on `Input` in [src/agents/livestream/mod.rs](src/agents/livestream/mod.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/agents/livestream/mod.rs](src/agents/livestream/mod.rs) -> `Input` (type)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `Input` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `Input` asserting distinct error discriminants for each failure class.
