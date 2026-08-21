# Q2428: Error type erasure in reset_mirror_calibration hides a security failure (plans/mod.rs)

## Question
Can an unprivileged attacker rely on `reset_mirror_calibration` in [src/plans/mod.rs](src/plans/mod.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `reset_mirror_calibration` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `reset_mirror_calibration` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `reset_mirror_calibration` asserting distinct error discriminants for each failure class.
