# [?] fix: rent_subnet_test: attempt to subtract with overflow (#8304)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-01-12
Source: https://github.com/dfinity/ic/commit/4963537f0a98056290734552dd4d255f8612a43a
Type: security-commit

## Details
fix: rent_subnet_test: attempt to subtract with overflow (#8304)

This fixes the `//rs/tests/nns:rent_subnet_test` which, after
70fb598fea6165ff9303b07777984ddbc27b0f95, started failing with:
```
2026-01-11 04:02:03.477 INFO[setup:StdErr] thread 'main' panicked at rs/tests/nns/rent_subnet_test.rs:638:9:
2026-01-11 04:02:03.477 INFO[setup:StdErr] attempt to subtract with overflow
```
We're not sure yet why 70fb598fea6165ff9303b07777984ddbc27b0f95
triggered this failure but we think it has something to do with the fact
that the test-driver is compiled with different options than before.
