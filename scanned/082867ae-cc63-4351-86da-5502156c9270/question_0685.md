# Q0685: Confidence/score not thresholded in version (rgb-net/lib.rs)

## Question
Can an unprivileged attacker exploit `version` in [rgb-net/src/lib.rs](rgb-net/src/lib.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [rgb-net/src/lib.rs](rgb-net/src/lib.rs) -> `version` (function)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `version` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `version` with low-confidence results asserting the decision is refused.
