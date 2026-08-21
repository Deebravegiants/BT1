# Q2284: Panic/abort policy in keep_file_descriptors (agents/mod.rs)

## Question
Can an unprivileged attacker induce a panic inside the task/thread managed by `keep_file_descriptors` in [src/agents/mod.rs](src/agents/mod.rs) so it is caught and the pipeline continues with that component's guarantee silently absent?

## Target
- File/function: [src/agents/mod.rs](src/agents/mod.rs) -> `keep_file_descriptors` (function)
- Entrypoint: Input that reliably panics the component
- Attacker controls: the panicking input
- Exploit idea: Check whether `keep_file_descriptors` converts a panic into a continue-with-default rather than a session abort.
- Invariant to test: A panicking security component aborts the session; it is never treated as optional.
- Expected Immunefi impact: Security component silently disabled by an attacker-induced panic
- Fast validation: Fault-injection test panicking the component and asserting session abort.
