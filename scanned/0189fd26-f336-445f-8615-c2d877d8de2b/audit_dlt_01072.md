# [M] soroban-sdk has overflow in Bytes::slice, Vec::slice, GenRange::gen_range for u64

## Summary
Severity: Medium
Chain: soroban-sdk
Component: soroban-sdk, soroban-sdk, soroban-sdk
CVE: CVE-2026-24889
CWE: Integer Overflow or Wraparound
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-96xm-fv9w-pf3f
Type: github-advisory

## Details
### Impact

Arithmetic overflow can be triggered in the `Bytes::slice`, `Vec::slice`, and `Prng::gen_range` (for `u64`) methods in the `soroban-sdk` in versions prior to and including `25.0.1`.

Contracts that pass user-controlled or computed range bounds to `Bytes::slice`, `Vec::slice`, or `Prng::gen_range` may silently operate on incorrect data ranges or generate random numbers from an unintended range, potentially resulting in corrupted contract state.

Note that the best practice when using the `soroban-sdk` and building Soroban contracts is to always enable `overflow-checks = true`. The `stellar contract init` tool that prepares the boiler plate for a Soroban contract, as well as all examples and docs, encourage the use of configuring `overflow-checks = true` on `release` profiles so that these arithmetic operations fail rather than silently wrap. Contracts are only impacted if they use `overflow-checks = false` either explicitly or implicitly. It is anticipated the majority of contracts could not be impacted because the best practice encouraged by tooling is to enable `overflow-checks`.

### Detail

When compiled with `overflow-checks = false` (the default for release builds), the bare arithmetic in those functions silently wraps on boundary values like `u32::MAX` or `u64::MAX`. This causes the range passed to the host to differ from the caller's intent:

`Bytes::slice`:
- `Bytes::slice(0..=u32::MAX)` — end `u32::MAX + 1` wraps to `0`, producing `slice(0..0)` returning empty instead of the full range.
- `Bytes::slice((Bound::Excluded(u32::MAX), Bound::Unbounded))` — start `u32::MAX + 1` wraps to `0`, producing `slice(0..)` instead of an empty/invalid range.

`Vec::slice`:
- `Vec::slice(0..=u32::MAX)` — same as `Bytes`, end wraps to `0`, returning empty.
- `Vec::slice((Bound::Excluded(u32::MAX), Bound::Unbounded))` — same as `Bytes`, start wraps to `0`.

`Prng::gen_range`:
- `Prng::gen_range((Bound::Unbounded, Bound::Excluded(0)))` — end `0 - 1` wraps to `u64::MAX`, producing range `0..=u64::MAX` instead of an empty/invalid range.
- `Prng::gen_range((Bound::Excluded(u64::MAX), Bound::Unbounded))` — start `u64::MAX + 1` wraps to `0`, producing range `0..=u64::MAX` instead of an empty/invalid range.

Note that some cases where the overflow was permitted and wrapped on the guest side are caught by the Soroban Env Host and cause a trap host side with error `HostError: Error(Object, IndexBounds)` `object index out of bounds`, because the wrapped values create invalid inputs:
- `Bytes::slice(u32::MAX..=u32::MAX)` — both start `u32::MAX + 1` and end `u32::MAX + 1` wrap to `0`, producing `slice(0..0)`.
- `Vec::slice(u32::MAX..=u32::MAX)` — same as `Bytes`, both wrap to `0`.


### Patches

The fix replaces bare arithmetic with `checked_add` / `checked_sub`, ensuring overflow traps regardless of the `overflow-checks` profile setting.

### Workarounds

Contract workspaces can be configured with the following profile to enable overflow checks on the arithmetic operations. This is the best practice when developing Soroban contracts, and the default if using the contract boilerplate generated using `stellar contract init`:

```toml
```

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-96xm-fv9w-pf3f_
