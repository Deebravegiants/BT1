# Q2937: Confidence/score not thresholded in Thumbnail (face_identifier/types.rs)

## Question
Can an unprivileged attacker exploit `Thumbnail` in [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) -> `Thumbnail` (type)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `Thumbnail` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `Thumbnail` with low-confidence results asserting the decision is refused.
