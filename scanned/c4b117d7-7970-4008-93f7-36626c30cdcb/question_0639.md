# Q0639: Non-determinism in is_face_detected makes a check unreproducible (python/rgb_net.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `is_face_detected` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `is_face_detected` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `is_face_detected` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `is_face_detected` N times on one input asserting identical output.
