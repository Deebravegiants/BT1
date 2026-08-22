# [?] fix(audit): bump rkyv to 0.8.16 to fix RUSTSEC-2026-0122 (#15709)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-05-11
Source: https://github.com/near/nearcore/commit/ca6c2d54ad5dd01f25ebeeb59fd505fa32e6f9ce
Type: security-commit

## Details
fix(audit): bump rkyv to 0.8.16 to fix RUSTSEC-2026-0122 (#15709)

Bump `rkyv` from 0.8.13 to 0.8.16 to address
[RUSTSEC-2026-0122](https://rustsec.org/advisories/RUSTSEC-2026-0122) —
panic safety bugs in `InlineVec::clear` and `SerVec::clear` that enable
arbitrary code execution. The advisory affects 0.8.0–0.8.15; 0.8.16
contains the patch.

Used transitively in the workspace via the `near-vm-*` crates. Caught by
`cargo audit` on #15708.
