# Q1754: Confidence/score not thresholded in init (face_identifier/mod.rs)

## Question
Can an unprivileged attacker exploit `init` in [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) -> `init` (function)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `init` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `init` with low-confidence results asserting the decision is refused.
