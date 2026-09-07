# [?] fix(chain): Return errors instead of panicking in methods for `Height`s (#7591)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-09-21
Source: https://github.com/ZcashFoundation/zebra/commit/daee5e5fcd738a4675369a9281a72eb764222c7f
Type: security-commit

## Details
fix(chain): Return errors instead of panicking in methods for `Height`s (#7591)

* Return errors instead of panicking

* Apply suggestions from code review

Co-authored-by: teor <teor@riseup.net>

* Turn `unwrap`s into `expect`s

* Refactor the error messages

---------

Co-authored-by: teor <teor@riseup.net>
