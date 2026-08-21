# Q3396: Error type erasure in poll_flush hides a security failure (agentwire/port.rs)

## Question
Can an unprivileged attacker rely on `poll_flush` in [agentwire/src/port.rs](agentwire/src/port.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `poll_flush` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `poll_flush` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `poll_flush` asserting distinct error discriminants for each failure class.
