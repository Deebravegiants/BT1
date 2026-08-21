# Q1112: Live stream started by keep_file_descriptors exposes capture content (agents/mod.rs)

## Question
Can an unprivileged attacker cause `keep_file_descriptors` in [src/agents/mod.rs](src/agents/mod.rs) to start or keep a live stream of camera content during another person's signup, so their face/iris frames are transmitted off-device outside the consented flow?

## Target
- File/function: [src/agents/mod.rs](src/agents/mod.rs) -> `keep_file_descriptors` (function)
- Entrypoint: Triggering the enable/keep-alive condition through normal flow
- Attacker controls: the condition or timing that keeps the stream enabled
- Exploit idea: Check `keep_file_descriptors` for a per-session consent gate and a guaranteed teardown on session end.
- Invariant to test: Camera streaming is gated on explicit consent and torn down on every session exit.
- Expected Immunefi impact: Non-consenting user's biometric video transmitted off-device
- Fast validation: Integration test asserting the stream is off in every state except explicit consent.
