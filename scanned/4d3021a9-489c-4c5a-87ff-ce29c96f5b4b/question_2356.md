# Q2356: ScanError accepts a stale or replayed scan across sessions (qr_scan/mod.rs)

## Question
Can an unprivileged attacker re-present a previously scanned code (their own, or one photographed from a prior session) so `ScanError` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) accepts it again without freshness or one-time-use enforcement, binding a second signup to that payload?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `ScanError` (type)
- Entrypoint: Re-presented QR payload
- Attacker controls: timing and repetition of an unmodified valid payload
- Exploit idea: Scan the same payload twice across sessions and check for nonce/expiry/consumed-marker enforcement in `ScanError`.
- Invariant to test: Each scanned credential is single-use and freshness-bound to exactly one signup session.
- Expected Immunefi impact: Replayed identity credential authorizing an additional signup
- Fast validation: Integration test: run the scan path twice with an identical payload and assert the second is rejected.
