# [?] Fix race condition around consensus state (#81)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-03-10
Source: https://github.com/sei-protocol/sei-chain/commit/5a62cf502a847c47c42dd2f4d75c203926b7cce1
Type: security-commit

## Details
Fix race condition around consensus state (#81)

* Fix race condition around consensus state

* Remove write lock since we already acquired it earlier

* Fix lock

---------

Co-authored-by: Yiming Zang <yzang@twitter.com>
