# Q2294: Panic/abort policy in poll_stream (livestream/upstream.rs)

## Question
Can an unprivileged attacker induce a panic inside the task/thread managed by `poll_stream` in [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) so it is caught and the pipeline continues with that component's guarantee silently absent?

## Target
- File/function: [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) -> `poll_stream` (function)
- Entrypoint: Input that reliably panics the component
- Attacker controls: the panicking input
- Exploit idea: Check whether `poll_stream` converts a panic into a continue-with-default rather than a session abort.
- Invariant to test: A panicking security component aborts the session; it is never treated as optional.
- Expected Immunefi impact: Security component silently disabled by an attacker-induced panic
- Fast validation: Fault-injection test panicking the component and asserting session abort.
