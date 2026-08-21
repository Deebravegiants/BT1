# Q0079: Error type erasure in do_signup hides a security failure (plans/mod.rs)

## Question
Can an unprivileged attacker rely on `do_signup` in [src/plans/mod.rs](src/plans/mod.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `do_signup` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `do_signup` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `do_signup` asserting distinct error discriminants for each failure class.
