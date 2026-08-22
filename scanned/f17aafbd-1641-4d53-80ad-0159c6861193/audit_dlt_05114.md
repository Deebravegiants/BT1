# [?] [backport] net: fix use-after-free in tests

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2023-01-05
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/14cab1395fc845c2b3f2c654e5a4f18958dc16df
Type: security-commit

## Details
[backport] net: fix use-after-free in tests

Summary
---

This is a backport of core#18376 that fixes a potential use-after-free.
Original commit message below from:
https://github.com/bitcoin/bitcoin/pull/18376/commits/7d8e1dec3b26074df1533f715871f79c956cc224

```
In PeerLogicValidation::PeerLogicValidation() we would schedule a lambda
function to execute later, capturing the local variable
`consensusParams` by reference.

Presumably this was considered safe because `consensusParams` is a
reference itself to a global variable which is not supposed to change,
but it can in tests.

Fixes #18372 (https://github.com/bitcoin/bitcoin/issues/18372)

```

Note: I was unable to reproduce the use-after-free seen by the core code, but
I only tried it with tsan and asan not with valgrind. After inspection
of the way our tests work with this class I do not believe there is any
UB possible here due to this mis-usage anyway in our current tests because
this class is torn down immediately after the tests cases that use it --
denialofservicetests -- finish executing (and immediately afterward the
scheduler is torn down as well).

Test Plan
---

- `ninja all check-all`
