# Q1884: Upload destination derived by HyraxCommitments not constrained (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker influence the destination host, bucket, region, or key that `HyraxCommitments` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) uploads biometric data to, so captured images or custody packages are written to a destination outside the authorized set?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `HyraxCommitments` (type)
- Entrypoint: Session-scoped fields that flow into the destination
- Attacker controls: region/key/name components reachable from their session
- Exploit idea: Check `HyraxCommitments` for an allowlist on destination host/bucket versus dynamic construction.
- Invariant to test: Upload destinations come from a fixed allowlist and are never composed from session data.
- Expected Immunefi impact: Biometric data exfiltrated to an attacker-influenced destination
- Fast validation: Unit-test `HyraxCommitments` with adversarial destination components asserting allowlist enforcement.
