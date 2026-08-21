# Q2915: Confidence/score not thresholded in EyeCenters (iris/types.rs)

## Question
Can an unprivileged attacker exploit `EyeCenters` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `EyeCenters` (type)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `EyeCenters` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `EyeCenters` with low-confidence results asserting the decision is refused.
