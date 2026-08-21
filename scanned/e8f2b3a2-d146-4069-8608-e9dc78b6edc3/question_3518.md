# Q3518: handle_qr_code logs or renders raw untrusted payload (qr_scan/mod.rs)

## Question
Can an unprivileged attacker cause `handle_qr_code` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) to persist or render the raw scanned payload (containing another user's identity token or network credential) into logs, UI, debug reports, or uploaded artifacts?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `handle_qr_code` (function)
- Entrypoint: Scanned payload that reaches logging/telemetry in the scan path
- Attacker controls: content of the payload, chosen to be a credential-bearing string
- Exploit idea: Trace `handle_qr_code`'s error and trace paths for full-payload formatting rather than redacted or hashed forms.
- Invariant to test: Credential-bearing scanned material is never emitted in cleartext to logs, UI, or uploaded artifacts.
- Expected Immunefi impact: Disclosure of identity/network credentials from a scanned code
- Fast validation: Unit-test `handle_qr_code` error paths and assert the payload appears only redacted.
