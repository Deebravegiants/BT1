# [M] stellar-xdr's StringM::from_str bypasses max length validation

## Summary
Severity: Medium
Chain: stellar-xdr
Component: stellar-xdr
CVE: CVE-2026-29795
CWE: Allocation of Resources Without Limits or Throttling
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-x57h-xx53-v53w
Type: github-advisory

## Details
### Impact

`StringM::from_str` does not validate that the input length is within the declared maximum (`MAX`). Calling `StringM::<N>::from_str(s)` where `s` is longer than `N` bytes succeeds and returns an `Ok` value instead of `Err(Error::LengthExceedsMax)`, producing a `StringM` that violates its length invariant.

This affects any code that constructs `StringM` values from string input using `FromStr` (including `str::parse`), and relies on the type's maximum length constraint being enforced. An oversized `StringM` could propagate through serialization, validation, or other logic that assumes the invariant holds.

All published versions of the `stellar-xdr` crate up to and including `v25.0.0` are affected.

### Patches

The fix is merged in [#500](https://github.com/stellar/rs-stellar-xdr/pull/500). It replaces the direct `Ok(Self(b))` construction with `b.try_into()`, which routes through `TryFrom<Vec<u8>>` and properly validates the length — matching the pattern already used by `BytesM::from_str`.

Users should upgrade to the first release containing this fix once published (the next release after `v25.0.0`).

### Workarounds

Validate the byte length of string input before calling `StringM::from_str`, or construct `StringM` values via `StringM::try_from(s.as_bytes().to_vec())` which correctly enforces the length constraint.

### References

- Issue: https://github.com/stellar/rs-stellar-xdr/issues/499
- Fix: https://github.com/stellar/rs-stellar-xdr/pull/500
