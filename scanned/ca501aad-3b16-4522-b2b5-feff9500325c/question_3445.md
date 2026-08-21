# Q3445: Error type erasure in spawn_process_impl hides a security failure (agent/process.rs)

## Question
Can an unprivileged attacker rely on `spawn_process_impl` in [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) -> `spawn_process_impl` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `spawn_process_impl` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `spawn_process_impl` asserting distinct error discriminants for each failure class.
