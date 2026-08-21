# Q2887: Confidence/score not thresholded in report_python_exception (python/mod.rs)

## Question
Can an unprivileged attacker exploit `report_python_exception` in [src/agents/python/mod.rs](src/agents/python/mod.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `report_python_exception` (function)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `report_python_exception` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `report_python_exception` with low-confidence results asserting the decision is refused.
