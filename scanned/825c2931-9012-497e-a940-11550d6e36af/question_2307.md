# Q2307: Live stream started by Vec2 exposes capture content (livestream-event/lib.rs)

## Question
Can an unprivileged attacker cause `Vec2` in [livestream-event/src/lib.rs](livestream-event/src/lib.rs) to start or keep a live stream of camera content during another person's signup, so their face/iris frames are transmitted off-device outside the consented flow?

## Target
- File/function: [livestream-event/src/lib.rs](livestream-event/src/lib.rs) -> `Vec2` (type)
- Entrypoint: Triggering the enable/keep-alive condition through normal flow
- Attacker controls: the condition or timing that keeps the stream enabled
- Exploit idea: Check `Vec2` for a per-session consent gate and a guaranteed teardown on session end.
- Invariant to test: Camera streaming is gated on explicit consent and torn down on every session exit.
- Expected Immunefi impact: Non-consenting user's biometric video transmitted off-device
- Fast validation: Integration test asserting the stream is off in every state except explicit consent.
