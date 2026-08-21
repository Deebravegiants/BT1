# Q2355: Newline/CRLF injection into config written from Plan (qr_scan/mod.rs)

## Question
Can an unprivileged attacker place CR/LF or a control-interface separator inside a QR field so `Plan` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) writes a multi-line entry that injects additional directives into the generated network/credential configuration?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `Plan` (type)
- Entrypoint: Scanned WiFi/provisioning QR
- Attacker controls: raw bytes of the SSID/passphrase/identity field including CR, LF, and quotes
- Exploit idea: Terminate the intended directive early and append a second attacker-chosen directive on the next line.
- Invariant to test: Untrusted values are serialized as single-line escaped literals and never expand the directive set.
- Expected Immunefi impact: Attacker-chosen configuration persisted on the Orb via a scanned code
- Fast validation: Fuzz `Plan` with control characters and assert the emitted config parses to exactly one directive.
