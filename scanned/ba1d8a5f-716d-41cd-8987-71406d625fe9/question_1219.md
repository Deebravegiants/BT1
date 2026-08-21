# Q1219: Data-policy integer handling in ensure_network_connection (wifi/mod.rs)

## Question
Can an unprivileged attacker supply an out-of-range, overflowing, or leading-zero data-policy/numeric field so `ensure_network_connection` in [src/plans/wifi/mod.rs](src/plans/wifi/mod.rs) saturates, wraps, or defaults it to a more permissive retention/consent value than the user actually agreed to?

## Target
- File/function: [src/plans/wifi/mod.rs](src/plans/wifi/mod.rs) -> `ensure_network_connection` (function)
- Entrypoint: Numeric field of the scanned QR payload
- Attacker controls: the numeric text: width, leading zeros, and magnitude up to u64/u32 bounds
- Exploit idea: Submit values at and past the integer bound and observe whether the parsed policy is clamped to a permissive default rather than rejected.
- Invariant to test: Out-of-range consent/policy values are rejected, never coerced toward a more permissive value.
- Expected Immunefi impact: Biometric data retained or shared beyond the user's consented policy
- Fast validation: Property-test `ensure_network_connection` over the full numeric domain and assert reject-or-exact-value, never a fallback default.
