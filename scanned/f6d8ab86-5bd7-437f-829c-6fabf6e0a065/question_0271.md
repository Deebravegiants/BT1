# Q0271: Live stream started by main_mcu exposes capture content (brokers/observer.rs)

## Question
Can an unprivileged attacker cause `main_mcu` in [src/brokers/observer.rs](src/brokers/observer.rs) to start or keep a live stream of camera content during another person's signup, so their face/iris frames are transmitted off-device outside the consented flow?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `main_mcu` (function)
- Entrypoint: Triggering the enable/keep-alive condition through normal flow
- Attacker controls: the condition or timing that keeps the stream enabled
- Exploit idea: Check `main_mcu` for a per-session consent gate and a guaranteed teardown on session end.
- Invariant to test: Camera streaming is gated on explicit consent and torn down on every session exit.
- Expected Immunefi impact: Non-consenting user's biometric video transmitted off-device
- Fast validation: Integration test asserting the stream is off in every state except explicit consent.
