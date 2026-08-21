# Q3104: Upload destination derived by save_frame_with_id not constrained (agents/image_notary.rs)

## Question
Can an unprivileged attacker influence the destination host, bucket, region, or key that `save_frame_with_id` in [src/agents/image_notary.rs](src/agents/image_notary.rs) uploads biometric data to, so captured images or custody packages are written to a destination outside the authorized set?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `save_frame_with_id` (function)
- Entrypoint: Session-scoped fields that flow into the destination
- Attacker controls: region/key/name components reachable from their session
- Exploit idea: Check `save_frame_with_id` for an allowlist on destination host/bucket versus dynamic construction.
- Invariant to test: Upload destinations come from a fixed allowlist and are never composed from session data.
- Expected Immunefi impact: Biometric data exfiltrated to an attacker-influenced destination
- Fast validation: Unit-test `save_frame_with_id` with adversarial destination components asserting allowlist enforcement.
