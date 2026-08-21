# Q0086: Error type erasure in scan_initial_qr_codes hides a security failure (plans/mod.rs)

## Question
Can an unprivileged attacker rely on `scan_initial_qr_codes` in [src/plans/mod.rs](src/plans/mod.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `scan_initial_qr_codes` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `scan_initial_qr_codes` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `scan_initial_qr_codes` asserting distinct error discriminants for each failure class.
