# Q1810: Confidence/score not thresholded in user_distance (python/rgb_net.rs)

## Question
Can an unprivileged attacker exploit `user_distance` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `user_distance` (function)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `user_distance` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `user_distance` with low-confidence results asserting the decision is refused.
