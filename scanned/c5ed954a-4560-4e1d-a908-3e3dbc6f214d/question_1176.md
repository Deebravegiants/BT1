# Q1176: Data-policy integer handling in poll_extra (qr_scan/mod.rs)

## Question
Can an unprivileged attacker supply an out-of-range, overflowing, or leading-zero data-policy/numeric field so `poll_extra` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) saturates, wraps, or defaults it to a more permissive retention/consent value than the user actually agreed to?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `poll_extra` (function)
- Entrypoint: Numeric field of the scanned QR payload
- Attacker controls: the numeric text: width, leading zeros, and magnitude up to u64/u32 bounds
- Exploit idea: Submit values at and past the integer bound and observe whether the parsed policy is clamped to a permissive default rather than rejected.
- Invariant to test: Out-of-range consent/policy values are rejected, never coerced toward a more permissive value.
- Expected Immunefi impact: Biometric data retained or shared beyond the user's consented policy
- Fast validation: Property-test `poll_extra` over the full numeric domain and assert reject-or-exact-value, never a fallback default.
