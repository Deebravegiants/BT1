# Q2378: Attacker-controlled QR text reaches process arguments via hex_string (network/mod.rs)

## Question
Can an unprivileged attacker embed shell/argument metacharacters or an option-looking token (e.g. a leading `-`) in a QR field so that `hex_string` in [src/network/mod.rs](src/network/mod.rs) forwards it into a child process, config file, or wpa_supplicant control command as an argument or directive?

## Target
- File/function: [src/network/mod.rs](src/network/mod.rs) -> `hex_string` (function)
- Entrypoint: Scanned QR payload propagated to the network/provisioning layer
- Attacker controls: full text of the SSID/password/identity field including metacharacters
- Exploit idea: Trace the field from `hex_string` to the command/config sink and check for quoting, escaping, or an allowlist.
- Invariant to test: No untrusted parsed value is ever interpolated into a command line, control-interface command, or config directive without escaping.
- Expected Immunefi impact: Attacker-directed command/config injection on the Orb from a scanned code
- Fast validation: Unit-test `hex_string` with metacharacter-laden fields and assert the sink receives them as inert literal data.
