# Q3557: Data-policy integer handling in parse_hidden (network/mecard.rs)

## Question
Can an unprivileged attacker supply an out-of-range, overflowing, or leading-zero data-policy/numeric field so `parse_hidden` in [src/network/mecard.rs](src/network/mecard.rs) saturates, wraps, or defaults it to a more permissive retention/consent value than the user actually agreed to?

## Target
- File/function: [src/network/mecard.rs](src/network/mecard.rs) -> `parse_hidden` (function)
- Entrypoint: Numeric field of the scanned QR payload
- Attacker controls: the numeric text: width, leading zeros, and magnitude up to u64/u32 bounds
- Exploit idea: Submit values at and past the integer bound and observe whether the parsed policy is clamped to a permissive default rather than rejected.
- Invariant to test: Out-of-range consent/policy values are rejected, never coerced toward a more permissive value.
- Expected Immunefi impact: Biometric data retained or shared beyond the user's consented policy
- Fast validation: Property-test `parse_hidden` over the full numeric domain and assert reject-or-exact-value, never a fallback default.
