# Q3149: Upload destination derived by NETWORK_MONITOR_HOST not constrained (backend/endpoints.rs)

## Question
Can an unprivileged attacker influence the destination host, bucket, region, or key that `NETWORK_MONITOR_HOST` in [src/backend/endpoints.rs](src/backend/endpoints.rs) uploads biometric data to, so captured images or custody packages are written to a destination outside the authorized set?

## Target
- File/function: [src/backend/endpoints.rs](src/backend/endpoints.rs) -> `NETWORK_MONITOR_HOST` (item)
- Entrypoint: Session-scoped fields that flow into the destination
- Attacker controls: region/key/name components reachable from their session
- Exploit idea: Check `NETWORK_MONITOR_HOST` for an allowlist on destination host/bucket versus dynamic construction.
- Invariant to test: Upload destinations come from a fixed allowlist and are never composed from session data.
- Expected Immunefi impact: Biometric data exfiltrated to an attacker-influenced destination
- Fast validation: Unit-test `NETWORK_MONITOR_HOST` with adversarial destination components asserting allowlist enforcement.
