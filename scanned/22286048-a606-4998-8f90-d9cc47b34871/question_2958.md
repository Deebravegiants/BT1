# Q2958: Stale result attribution in warmup (python/ir_net.rs)

## Question
Can an unprivileged attacker exploit `warmup` in [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) matching an inference result to the current frame/subject by arrival order rather than by an explicit request id, so a late result is attributed to a newer frame?

## Target
- File/function: [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) -> `warmup` (function)
- Entrypoint: Varying scene complexity to vary inference latency
- Attacker controls: per-frame inference latency via scene complexity
- Exploit idea: Check `warmup` for request/response correlation identifiers.
- Invariant to test: Every inference result is bound to its exact input by an explicit identifier.
- Expected Immunefi impact: Fraud/identity decision applied to the wrong frame or subject
- Fast validation: Concurrency test with reordered results asserting correlation-id matching.
