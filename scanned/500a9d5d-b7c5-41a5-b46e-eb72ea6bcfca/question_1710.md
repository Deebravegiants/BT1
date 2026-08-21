# Q1710: Mixed-subject capture set through LiquidLensController (agents/ir_auto_focus.rs)

## Question
Can an unprivileged attacker swap subjects mid-capture so `LiquidLensController` in [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) assembles a set containing frames from two different people, with no identity-continuity check binding all frames to one subject?

## Target
- File/function: [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) -> `LiquidLensController` (type)
- Entrypoint: Two people alternating in front of the sensor during capture
- Attacker controls: the moment of the swap relative to the capture window
- Exploit idea: Check whether `LiquidLensController` verifies continuity/identity consistency across the frames it aggregates.
- Invariant to test: All frames in a capture set are proven to come from one continuously tracked subject.
- Expected Immunefi impact: Biometric record blending two identities, corrupting uniqueness guarantees
- Fast validation: Integration test feeding a two-subject frame sequence and asserting rejection.
