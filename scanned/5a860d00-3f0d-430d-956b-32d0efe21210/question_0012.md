# Q0012: Attacker-controlled QR text reaches process arguments via ScanError (qr_scan/mod.rs)

## Question
Can an unprivileged attacker embed shell/argument metacharacters or an option-looking token (e.g. a leading `-`) in a QR field so that `ScanError` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) forwards it into a child process, config file, or wpa_supplicant control command as an argument or directive?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `ScanError` (type)
- Entrypoint: Scanned QR payload propagated to the network/provisioning layer
- Attacker controls: full text of the SSID/password/identity field including metacharacters
- Exploit idea: Trace the field from `ScanError` to the command/config sink and check for quoting, escaping, or an allowlist.
- Invariant to test: No untrusted parsed value is ever interpolated into a command line, control-interface command, or config directive without escaping.
- Expected Immunefi impact: Attacker-directed command/config injection on the Orb from a scanned code
- Fast validation: Unit-test `ScanError` with metacharacter-laden fields and assert the sink receives them as inert literal data.
