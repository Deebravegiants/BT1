# Q1278: Panic/abort policy in has_biometric_input (plans/mod.rs)

## Question
Can an unprivileged attacker induce a panic inside the task/thread managed by `has_biometric_input` in [src/plans/mod.rs](src/plans/mod.rs) so it is caught and the pipeline continues with that component's guarantee silently absent?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `has_biometric_input` (function)
- Entrypoint: Input that reliably panics the component
- Attacker controls: the panicking input
- Exploit idea: Check whether `has_biometric_input` converts a panic into a continue-with-default rather than a session abort.
- Invariant to test: A panicking security component aborts the session; it is never treated as optional.
- Expected Immunefi impact: Security component silently disabled by an attacker-induced panic
- Fast validation: Fault-injection test panicking the component and asserting session abort.
