# Q2907: Confidence/score not thresholded in serialized_mask (iris/types.rs)

## Question
Can an unprivileged attacker exploit `serialized_mask` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `serialized_mask` (function)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `serialized_mask` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `serialized_mask` with low-confidence results asserting the decision is refused.
