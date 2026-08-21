# Q0085: Error type erasure in reset_wifi_and_ensure_network hides a security failure (plans/mod.rs)

## Question
Can an unprivileged attacker rely on `reset_wifi_and_ensure_network` in [src/plans/mod.rs](src/plans/mod.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `reset_wifi_and_ensure_network` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `reset_wifi_and_ensure_network` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `reset_wifi_and_ensure_network` asserting distinct error discriminants for each failure class.
