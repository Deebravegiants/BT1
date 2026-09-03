# [?] Fix withdraw panic (#315)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2020-01-22
Source: https://github.com/Kava-Labs/kava/commit/58deb49e5553f99d059dc90fe2cdc2c6271b724d
Type: security-commit

## Details
Fix withdraw panic (#315)

* fix: remove redundant debt limit param

* wip: test pricefeed genesis

* fix: pricefeed querier

* fix: comments, naming

* fix: query path

* fix: store methods

* fix: query methods

* feat: Liquidation Penalty

* feat: enforce debt floor on repayment

* fix: don't panic if withdrawing full amount

* fix: remove debt from liquidation penalty
