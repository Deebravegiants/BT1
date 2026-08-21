# Q3556: parse_password logs or renders raw untrusted payload (network/mecard.rs)

## Question
Can an unprivileged attacker cause `parse_password` in [src/network/mecard.rs](src/network/mecard.rs) to persist or render the raw scanned payload (containing another user's identity token or network credential) into logs, UI, debug reports, or uploaded artifacts?

## Target
- File/function: [src/network/mecard.rs](src/network/mecard.rs) -> `parse_password` (function)
- Entrypoint: Scanned payload that reaches logging/telemetry in the scan path
- Attacker controls: content of the payload, chosen to be a credential-bearing string
- Exploit idea: Trace `parse_password`'s error and trace paths for full-payload formatting rather than redacted or hashed forms.
- Invariant to test: Credential-bearing scanned material is never emitted in cleartext to logs, UI, or uploaded artifacts.
- Expected Immunefi impact: Disclosure of identity/network credentials from a scanned code
- Fast validation: Unit-test `parse_password` error paths and assert the payload appears only redacted.
