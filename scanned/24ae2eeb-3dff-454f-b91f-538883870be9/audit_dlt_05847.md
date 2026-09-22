# [?] fix(systest): broader allowed panic sources in system tests (#10102)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-05-06
Source: https://github.com/dfinity/ic/commit/72c7f3be1013f0e1f7ee814f92aca8140130cf33
Type: security-commit

## Details
fix(systest): broader allowed panic sources in system tests (#10102)

https://github.com/dfinity/ic/pull/10041 added a new allowed panic
pattern but did not add its original location in
`sandboxed_execution_controller.rs` to the allowed pattern, flaking
tests using mainnet versions.
