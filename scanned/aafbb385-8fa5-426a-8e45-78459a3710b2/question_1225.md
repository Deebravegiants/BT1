# Q1225: check_hex_string_format accepts a stale or replayed scan across sessions (wpa-supplicant-interface/join.rs)

## Question
Can an unprivileged attacker re-present a previously scanned code (their own, or one photographed from a prior session) so `check_hex_string_format` in [wpa-supplicant-interface/src/join.rs](wpa-supplicant-interface/src/join.rs) accepts it again without freshness or one-time-use enforcement, binding a second signup to that payload?

## Target
- File/function: [wpa-supplicant-interface/src/join.rs](wpa-supplicant-interface/src/join.rs) -> `check_hex_string_format` (function)
- Entrypoint: Re-presented QR payload
- Attacker controls: timing and repetition of an unmodified valid payload
- Exploit idea: Scan the same payload twice across sessions and check for nonce/expiry/consumed-marker enforcement in `check_hex_string_format`.
- Invariant to test: Each scanned credential is single-use and freshness-bound to exactly one signup session.
- Expected Immunefi impact: Replayed identity credential authorizing an additional signup
- Fast validation: Integration test: run the scan path twice with an identical payload and assert the second is rejected.
