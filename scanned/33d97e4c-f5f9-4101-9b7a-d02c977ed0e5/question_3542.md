# Q3542: initializer logs or renders raw untrusted payload (agents/qr_code.rs)

## Question
Can an unprivileged attacker cause `initializer` in [src/agents/qr_code.rs](src/agents/qr_code.rs) to persist or render the raw scanned payload (containing another user's identity token or network credential) into logs, UI, debug reports, or uploaded artifacts?

## Target
- File/function: [src/agents/qr_code.rs](src/agents/qr_code.rs) -> `initializer` (function)
- Entrypoint: Scanned payload that reaches logging/telemetry in the scan path
- Attacker controls: content of the payload, chosen to be a credential-bearing string
- Exploit idea: Trace `initializer`'s error and trace paths for full-payload formatting rather than redacted or hashed forms.
- Invariant to test: Credential-bearing scanned material is never emitted in cleartext to logs, UI, or uploaded artifacts.
- Expected Immunefi impact: Disclosure of identity/network credentials from a scanned code
- Fast validation: Unit-test `initializer` error paths and assert the payload appears only redacted.
