# Q3453: Panic/abort policy in spawn_thread (agent/thread.rs)

## Question
Can an unprivileged attacker induce a panic inside the task/thread managed by `spawn_thread` in [agentwire/src/agent/thread.rs](agentwire/src/agent/thread.rs) so it is caught and the pipeline continues with that component's guarantee silently absent?

## Target
- File/function: [agentwire/src/agent/thread.rs](agentwire/src/agent/thread.rs) -> `spawn_thread` (function)
- Entrypoint: Input that reliably panics the component
- Attacker controls: the panicking input
- Exploit idea: Check whether `spawn_thread` converts a panic into a continue-with-default rather than a session abort.
- Invariant to test: A panicking security component aborts the session; it is never treated as optional.
- Expected Immunefi impact: Security component silently disabled by an attacker-induced panic
- Fast validation: Fault-injection test panicking the component and asserting session abort.
