# Q3194: Upload destination derived by Response not constrained (backend/presigned_url.rs)

## Question
Can an unprivileged attacker influence the destination host, bucket, region, or key that `Response` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) uploads biometric data to, so captured images or custody packages are written to a destination outside the authorized set?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `Response` (type)
- Entrypoint: Session-scoped fields that flow into the destination
- Attacker controls: region/key/name components reachable from their session
- Exploit idea: Check `Response` for an allowlist on destination host/bucket versus dynamic construction.
- Invariant to test: Upload destinations come from a fixed allowlist and are never composed from session data.
- Expected Immunefi impact: Biometric data exfiltrated to an attacker-influenced destination
- Fast validation: Unit-test `Response` with adversarial destination components asserting allowlist enforcement.
