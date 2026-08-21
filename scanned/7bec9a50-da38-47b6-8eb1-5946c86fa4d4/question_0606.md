# Q0606: Confidence/score not thresholded in run (python/occlusion.rs)

## Question
Can an unprivileged attacker exploit `run` in [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) -> `run` (function)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `run` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `run` with low-confidence results asserting the decision is refused.
