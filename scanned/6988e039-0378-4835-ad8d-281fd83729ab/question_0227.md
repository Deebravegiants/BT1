# Q0227: Panic/abort policy in init_ir_face_camera (brokers/orb.rs)

## Question
Can an unprivileged attacker induce a panic inside the task/thread managed by `init_ir_face_camera` in [src/brokers/orb.rs](src/brokers/orb.rs) so it is caught and the pipeline continues with that component's guarantee silently absent?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `init_ir_face_camera` (function)
- Entrypoint: Input that reliably panics the component
- Attacker controls: the panicking input
- Exploit idea: Check whether `init_ir_face_camera` converts a panic into a continue-with-default rather than a session abort.
- Invariant to test: A panicking security component aborts the session; it is never treated as optional.
- Expected Immunefi impact: Security component silently disabled by an attacker-induced panic
- Fast validation: Fault-injection test panicking the component and asserting session abort.
