# Q2443: Live stream started by after_signup exposes capture content (plans/mod.rs)

## Question
Can an unprivileged attacker cause `after_signup` in [src/plans/mod.rs](src/plans/mod.rs) to start or keep a live stream of camera content during another person's signup, so their face/iris frames are transmitted off-device outside the consented flow?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `after_signup` (function)
- Entrypoint: Triggering the enable/keep-alive condition through normal flow
- Attacker controls: the condition or timing that keeps the stream enabled
- Exploit idea: Check `after_signup` for a per-session consent gate and a guaranteed teardown on session end.
- Invariant to test: Camera streaming is gated on explicit consent and torn down on every session exit.
- Expected Immunefi impact: Non-consenting user's biometric video transmitted off-device
- Fast validation: Integration test asserting the stream is off in every state except explicit consent.
