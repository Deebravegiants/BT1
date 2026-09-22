# [?] fix(state): Avoid panics and history tree consensus database concurrency bugs  (#7590)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-09-20
Source: https://github.com/ZcashFoundation/zebra/commit/2dce6862a056957b5093f3659d46e4ce09e69978
Type: security-commit

## Details
fix(state): Avoid panics and history tree consensus database concurrency bugs  (#7590)

* Add a RawBytes database serialization type

* Fix a history tree database concurrency bug

* Fix a sprout tree concurrency panic
