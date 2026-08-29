# [?] fix(lnv2): make PaymentFee Add overflow explicit (#8948)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-04
Source: https://github.com/fedimint/fedimint/commit/46ed0e6ae9dc75291df66bfa9a47e8508e884159
Type: security-commit

## Details
fix(lnv2): make PaymentFee Add overflow explicit (#8948)

## Summary

Make `PaymentFee + PaymentFee` use checked arithmetic internally and
panic with explicit `expect` messages on overflow. This keeps the
existing `Add` API while making the failure deterministic in release
builds.

## Details

This is the smaller alternative requested in #8941: instead of adding
`checked_add` call-site plumbing, the invariant stays inside the `Add`
impl. Overflow should only be reachable from operator-provided extreme
fee configuration, so a loud invariant failure is preferable to
release-build wrapping.

## Testing

- [x] `just format`
- [x] `cargo check -q -p fedimint-lnv2-common`
- [x] `cargo test -q -p fedimint-lnv2-common payment_fee_add_panics_on`
- [x] `cargo test --release -q -p fedimint-lnv2-common
payment_fee_add_panics_on`
- [x] `cargo clippy -q -p fedimint-lnv2-common --all-targets -- -D
warnings`
- [ ] `just final-lint` (blocked locally: offline clippy could not find
cached `ahash v0.8.12`)

Follow-up to #8941.
