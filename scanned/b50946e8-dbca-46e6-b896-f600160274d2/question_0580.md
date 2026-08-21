# Q0580: Stale result attribution in is_valid (face_identifier/mod.rs)

## Question
Can an unprivileged attacker exploit `is_valid` in [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) matching an inference result to the current frame/subject by arrival order rather than by an explicit request id, so a late result is attributed to a newer frame?

## Target
- File/function: [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) -> `is_valid` (function)
- Entrypoint: Varying scene complexity to vary inference latency
- Attacker controls: per-frame inference latency via scene complexity
- Exploit idea: Check `is_valid` for request/response correlation identifiers.
- Invariant to test: Every inference result is bound to its exact input by an explicit identifier.
- Expected Immunefi impact: Fraud/identity decision applied to the wrong frame or subject
- Fast validation: Concurrency test with reordered results asserting correlation-id matching.
