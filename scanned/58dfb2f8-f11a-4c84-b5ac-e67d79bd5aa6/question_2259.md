# Q2259: Error type erasure in enabled hides a security failure (agent/mod.rs)

## Question
Can an unprivileged attacker rely on `enabled` in [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) -> `enabled` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `enabled` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `enabled` asserting distinct error discriminants for each failure class.
