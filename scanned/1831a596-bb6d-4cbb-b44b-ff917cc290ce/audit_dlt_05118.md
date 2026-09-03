# [?] [backport] test: add BIP37 remote crash bug [CVE-2013-5700] test to p2p_filter.py

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2020-04-03
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/4d76dd59fd6562371a0daaeffe922a21304e5e87
Type: security-commit

## Details
[backport] test: add BIP37 remote crash bug [CVE-2013-5700] test to p2p_filter.py

Summary
---

This is a backport of https://github.com/bitcoin/bitcoin/pull/18515/commits/0ed2d8e07d3806d78d03a77d2153f22f9d733a07

Test plan
---

* `ninja all`
* `./test/functional/test_runner.py p2p_filter.py`
