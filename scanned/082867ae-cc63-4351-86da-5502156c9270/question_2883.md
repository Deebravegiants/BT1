# Q2883: Confidence/score not thresholded in DerivedSignal (agents/ir_auto_focus.rs)

## Question
Can an unprivileged attacker exploit `DerivedSignal` in [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) -> `DerivedSignal` (type)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `DerivedSignal` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `DerivedSignal` with low-confidence results asserting the decision is refused.
