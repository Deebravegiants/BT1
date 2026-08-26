# [?] fix(governance): don't panic when a node provider has no id (#11092)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-08-13
Source: https://github.com/dfinity/ic/commit/8be8631fa4cce7784d6da714cbeea6711a0f5e45
Type: security-commit

## Details
fix(governance): don't panic when a node provider has no id (#11092)

`validate_assign_noid_payload` was calling `.unwrap()` on `np.id`, which
is an `Option`. If any node provider in governance state has `id =
None`, this panics and blocks all `AddNodeOperator` proposal
submissions.

Fixed by comparing the `Option` values directly instead of unwrapping
them.
