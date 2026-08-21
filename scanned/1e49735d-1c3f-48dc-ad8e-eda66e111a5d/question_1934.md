# Q1934: Upload destination derived by ssd_save_png not constrained (agents/image_notary.rs)

## Question
Can an unprivileged attacker influence the destination host, bucket, region, or key that `ssd_save_png` in [src/agents/image_notary.rs](src/agents/image_notary.rs) uploads biometric data to, so captured images or custody packages are written to a destination outside the authorized set?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `ssd_save_png` (function)
- Entrypoint: Session-scoped fields that flow into the destination
- Attacker controls: region/key/name components reachable from their session
- Exploit idea: Check `ssd_save_png` for an allowlist on destination host/bucket versus dynamic construction.
- Invariant to test: Upload destinations come from a fixed allowlist and are never composed from session data.
- Expected Immunefi impact: Biometric data exfiltrated to an attacker-influenced destination
- Fast validation: Unit-test `ssd_save_png` with adversarial destination components asserting allowlist enforcement.
