# [?] [DEC-2075] [fix-halt] Avoid overflow in vest and rewards stats (#530)

## Summary
Severity: Unknown
Chain: dYdX
Component: dydxprotocol/v4-chain
Published: 2023-10-09
Source: https://github.com/dydxprotocol/v4-chain/commit/6eceae2125b48e311e0bf3153abb45f4ecbc322c
Type: security-commit

## Details
[DEC-2075] [fix-halt] Avoid overflow in vest and rewards stats (#530)

* avoid int64 oerflow

* divide amount before casting, add test

* change log unit

* nit

* remove debug print

* use `GetMetricValueFromBigInt`

* nits

* also update how totalrewardweight is emitted

* nits
