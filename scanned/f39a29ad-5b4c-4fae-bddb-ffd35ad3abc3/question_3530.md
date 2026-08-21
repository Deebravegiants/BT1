# Q3530: from_v2 logs or renders raw untrusted payload (qr_scan/user.rs)

## Question
Can an unprivileged attacker cause `from_v2` in [src/plans/qr_scan/user.rs](src/plans/qr_scan/user.rs) to persist or render the raw scanned payload (containing another user's identity token or network credential) into logs, UI, debug reports, or uploaded artifacts?

## Target
- File/function: [src/plans/qr_scan/user.rs](src/plans/qr_scan/user.rs) -> `from_v2` (function)
- Entrypoint: Scanned payload that reaches logging/telemetry in the scan path
- Attacker controls: content of the payload, chosen to be a credential-bearing string
- Exploit idea: Trace `from_v2`'s error and trace paths for full-payload formatting rather than redacted or hashed forms.
- Invariant to test: Credential-bearing scanned material is never emitted in cleartext to logs, UI, or uploaded artifacts.
- Expected Immunefi impact: Disclosure of identity/network credentials from a scanned code
- Fast validation: Unit-test `from_v2` error paths and assert the payload appears only redacted.
