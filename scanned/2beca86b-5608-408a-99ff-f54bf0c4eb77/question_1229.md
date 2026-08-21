# Q1229: recover_config logs or renders raw untrusted payload (wpa-supplicant-interface/status.rs)

## Question
Can an unprivileged attacker cause `recover_config` in [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) to persist or render the raw scanned payload (containing another user's identity token or network credential) into logs, UI, debug reports, or uploaded artifacts?

## Target
- File/function: [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) -> `recover_config` (function)
- Entrypoint: Scanned payload that reaches logging/telemetry in the scan path
- Attacker controls: content of the payload, chosen to be a credential-bearing string
- Exploit idea: Trace `recover_config`'s error and trace paths for full-payload formatting rather than redacted or hashed forms.
- Invariant to test: Credential-bearing scanned material is never emitted in cleartext to logs, UI, or uploaded artifacts.
- Expected Immunefi impact: Disclosure of identity/network credentials from a scanned code
- Fast validation: Unit-test `recover_config` error paths and assert the payload appears only redacted.
