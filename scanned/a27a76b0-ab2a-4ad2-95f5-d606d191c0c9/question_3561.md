# Q3561: Newline/CRLF injection into config written from AuthType (network/mecard.rs)

## Question
Can an unprivileged attacker place CR/LF or a control-interface separator inside a QR field so `AuthType` in [src/network/mecard.rs](src/network/mecard.rs) writes a multi-line entry that injects additional directives into the generated network/credential configuration?

## Target
- File/function: [src/network/mecard.rs](src/network/mecard.rs) -> `AuthType` (type)
- Entrypoint: Scanned WiFi/provisioning QR
- Attacker controls: raw bytes of the SSID/passphrase/identity field including CR, LF, and quotes
- Exploit idea: Terminate the intended directive early and append a second attacker-chosen directive on the next line.
- Invariant to test: Untrusted values are serialized as single-line escaped literals and never expand the directive set.
- Expected Immunefi impact: Attacker-chosen configuration persisted on the Orb via a scanned code
- Fast validation: Fuzz `AuthType` with control characters and assert the emitted config parses to exactly one directive.
