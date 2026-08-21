# Q3573: Field-count/regex laxity in recover_config enables field injection (wpa-supplicant-interface/status.rs)

## Question
Can an unprivileged attacker inject an extra delimiter or field into the QR payload so `recover_config` in [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) parses attacker-appended fields (extension flags, data policy, mode selectors) that were never granted for their session?

## Target
- File/function: [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) -> `recover_config` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: delimiter placement and the number/order of payload fields
- Exploit idea: Append or reorder `:`-separated segments so the regex/parser binds attacker values into optional fields and silently upgrades session capabilities.
- Invariant to test: Only fields the operator/backend authorized are parseable; unknown or extra fields cause hard rejection, never silent acceptance.
- Expected Immunefi impact: Unauthorized capability or data-policy escalation for the attacker's signup
- Fast validation: Unit-test `recover_config` with appended/duplicated segments and assert rejection instead of partial parse.
