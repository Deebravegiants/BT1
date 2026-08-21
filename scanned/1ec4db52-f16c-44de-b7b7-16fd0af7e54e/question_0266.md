# Q0266: Panic/abort policy in poll_status_update (brokers/observer.rs)

## Question
Can an unprivileged attacker induce a panic inside the task/thread managed by `poll_status_update` in [src/brokers/observer.rs](src/brokers/observer.rs) so it is caught and the pipeline continues with that component's guarantee silently absent?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `poll_status_update` (function)
- Entrypoint: Input that reliably panics the component
- Attacker controls: the panicking input
- Exploit idea: Check whether `poll_status_update` converts a panic into a continue-with-default rather than a session abort.
- Invariant to test: A panicking security component aborts the session; it is never treated as optional.
- Expected Immunefi impact: Security component silently disabled by an attacker-induced panic
- Fast validation: Fault-injection test panicking the component and asserting session abort.
