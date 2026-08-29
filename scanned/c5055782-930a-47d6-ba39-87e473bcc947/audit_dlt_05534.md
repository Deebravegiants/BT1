# [?] fix reward distribution module overflow (#1859)

## Summary
Severity: Unknown
Chain: Synthetix
Component: Synthetixio/synthetix-v3
Published: 2023-10-11
Source: https://github.com/Synthetixio/synthetix-v3/commit/9b6781de293b7939f72f5d1f3607f5da12ab7fa4
Type: security-commit

## Details
fix reward distribution module overflow (#1859)

* fix reward distribution module overflow

caused by data type size 128 instead of 256 in a big number
multiplication operation

* add and fix tests

* fix

* Revert "add and fix tests"

This reverts commit 059b9282ff45fab5d41ffd90e0184e1c9342a357.

---------

Co-authored-by: jmzwar <james@jmzwar.com>
