# Q1420: Live stream started by StateTx exposes capture content (brokers/orb.rs)

## Question
Can an unprivileged attacker cause `StateTx` in [src/brokers/orb.rs](src/brokers/orb.rs) to start or keep a live stream of camera content during another person's signup, so their face/iris frames are transmitted off-device outside the consented flow?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `StateTx` (type)
- Entrypoint: Triggering the enable/keep-alive condition through normal flow
- Attacker controls: the condition or timing that keeps the stream enabled
- Exploit idea: Check `StateTx` for a per-session consent gate and a guaranteed teardown on session end.
- Invariant to test: Camera streaming is gated on explicit consent and torn down on every session exit.
- Expected Immunefi impact: Non-consenting user's biometric video transmitted off-device
- Fast validation: Integration test asserting the stream is off in every state except explicit consent.
