# Q2884: Confidence/score not thresholded in choose_config (python/mod.rs)

## Question
Can an unprivileged attacker exploit `choose_config` in [src/agents/python/mod.rs](src/agents/python/mod.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `choose_config` (function)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `choose_config` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `choose_config` with low-confidence results asserting the decision is refused.
