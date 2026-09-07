# [?] refactor/security: prevent same execution price exploit within the same ULP (#5693)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-07-02
Source: https://github.com/osmosis-labs/osmosis/commit/cf223be21b8530b28a326c4d0738e8dc5d0f63f2
Type: security-commit

## Details
refactor/security: prevent same execution price exploit within the same ULP (#5693)

* repro infinite loop in swap logic

* precision increase solution to infinite loop bug

* fix

* remove logic

* remove error

* updates

* updates

* updates

* updates

* begin switching zeroForOneStrategy.ComputeSwapWithinBucketInGivenOut

* switch remaining zero for one swap step and add rounding comments

* begin switching cur sqrt price to big dec in swaps

* try adding CalculateSqrtPriceToTickBigDec

* one for zero out given in tests

* fix one for zero tests

* update one for zero tests

* in-progress test

* updates


_Trimmed to 38 lines — full report: https://github.com/osmosis-labs/osmosis/commit/cf223be21b8530b28a326c4d0738e8dc5d0f63f2_
