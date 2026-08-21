# Q1095: Panic/abort policy in spawn_process (agent/process.rs)

## Question
Can an unprivileged attacker induce a panic inside the task/thread managed by `spawn_process` in [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) so it is caught and the pipeline continues with that component's guarantee silently absent?

## Target
- File/function: [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) -> `spawn_process` (function)
- Entrypoint: Input that reliably panics the component
- Attacker controls: the panicking input
- Exploit idea: Check whether `spawn_process` converts a panic into a continue-with-default rather than a session abort.
- Invariant to test: A panicking security component aborts the session; it is never treated as optional.
- Expected Immunefi impact: Security component silently disabled by an attacker-induced panic
- Fast validation: Fault-injection test panicking the component and asserting session abort.
