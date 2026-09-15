# [?] Fix tmpdir-reuse crash bug of new QIC (#4820)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2025-07-08
Source: https://github.com/stellar/stellar-core/commit/9360433ba93f1eb632da57086017f49c302475ff
Type: security-commit

## Details
Fix tmpdir-reuse crash bug of new QIC (#4820)

This is a slightly expanded version of
https://github.com/stellar/stellar-core/pull/4818 with a test and a
little bit of cleanup / robustness around resetting the tmpdir
aggressively.

There's plenty of room for more cleanup here -- the cluster of classes
is fairly fragile and un-encapsulated still -- but this ought to unblock
us for the current release.
