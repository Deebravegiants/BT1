# Q2313: Error type erasure in debug_any hides a security failure (orb-relay-client/lib.rs)

## Question
Can an unprivileged attacker rely on `debug_any` in [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) -> `debug_any` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `debug_any` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `debug_any` asserting distinct error discriminants for each failure class.
