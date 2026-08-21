# Q0329: Stale result attribution in update_occlusion (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker exploit `update_occlusion` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) matching an inference result to the current frame/subject by arrival order rather than by an explicit request id, so a late result is attributed to a newer frame?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `update_occlusion` (function)
- Entrypoint: Varying scene complexity to vary inference latency
- Attacker controls: per-frame inference latency via scene complexity
- Exploit idea: Check `update_occlusion` for request/response correlation identifiers.
- Invariant to test: Every inference result is bound to its exact input by an explicit identifier.
- Expected Immunefi impact: Fraud/identity decision applied to the wrong frame or subject
- Fast validation: Concurrency test with reordered results asserting correlation-id matching.
