# Q0621: Confidence/score not thresholded in extract (python/ir_net.rs)

## Question
Can an unprivileged attacker exploit `extract` in [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) -> `extract` (function)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `extract` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `extract` with low-confidence results asserting the decision is refused.
