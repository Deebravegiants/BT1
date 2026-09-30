# [M] Potentially Incorrect Output of Constant-Time Swap/Select on Aarch64

## Summary
Severity: Medium
Advisory: RUSTSEC-2026-0212
Ecosystem: crates.io
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0212
Type: osv

## Affected
- crates.io: `libcrux-secrets` — affected >=0.0.0-0 <0.0.6

## Details
The implementation of constant-time swap and select on aarch64
platforms used a `cmp` instruction in inline assembly to check whether
an 8-bit wide selector was 0. The `cmp` instruction works on 32-bit
registers, which included the unspecified high 24 bits of the `cmp` operand.
Depending on the execution environment the `cmp`
could thus potentially return an incorrect result because its
operand's high bits in the inline assembly were set when Rust expected them to be unset.
This could lead to incorrect results for the constant-time swap and select
operations built from this comparison.

## Impact
In certain circumstances the swap and select instructions on aarch64
platforms returned incorrect results.

## Mitigation
Starting from version `0.0.6`, the selector is compared using a `tst`
instruction with a mask, which only compares the first 8 bits of the
selector.

## References
- https://crates.io/crates/libcrux-secrets
- https://rustsec.org/advisories/RUSTSEC-2026-0212.html
- https://github.com/celabshq/libcrux/pull/1461
