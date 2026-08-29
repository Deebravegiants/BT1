# [?] Merge #7236: fix: resolve signed integer overflow UB in CoinJoin priority and timeout

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-03-26
Source: https://github.com/dashpay/dash/commit/d1eab6cc24bb4f622d2d5e85bad5d108480ec079
Type: security-commit

## Details
Merge #7236: fix: resolve signed integer overflow UB in CoinJoin priority and timeout

e8ec63a1e090f4e6bcdfa3cd48891c8672b51433 test: add regression tests for CoinJoin UB fixes (PastaClaw)
817234fa94538383a8957561bec5c4e073cd7d3a fix: resolve signed integer overflow UB in CoinJoin priority and timeout (PastaClaw)

Pull request description:

  ## Summary

  Fix two signed integer overflow UB issues in CoinJoin code, found during fuzz testing.

  ### `CalculateAmountPriority` (common.h)

  The return type is `int` but the computation `-(nInputAmount / COIN)` operates on
  `int64_t` values. When `nInputAmount` is extremely large (e.g. near `MAX_MONEY`),
  the result exceeds `INT_MAX` and the implicit narrowing to `int` is undefined
  behavior under UBSan.

  **Fix:** Clamp the `int64_t` result to `[INT_MIN, INT_MAX]` before returning.
  This preserves the existing sort ordering for all realistic inputs while making
  extreme values well-defined.

  ### `IsTimeOutOfBounds` (coinjoin.cpp)

  The expression `current_time - nTime` overflows when the two `int64_t` values
  differ by more than `INT64_MAX` (e.g. one large positive, one large negative).

  **Fix:** Compute the absolute difference using unsigned arithmetic, which is
  well-defined for all inputs.

  ## Validation

  - Both functions are non-consensus (CoinJoin sort priority and queue timeout only)
  - Neither overflow is exploitable — CoinJoin queue entries require valid MN signatures,
    and the priority function only affects local sort order
  - The fixes preserve identical behavior for all realistic inputs
  - Found via UBSan-instrumented fuzz testing on the `ci/fuzz-regression` branch


_Trimmed to 38 lines — full report: https://github.com/dashpay/dash/commit/d1eab6cc24bb4f622d2d5e85bad5d108480ec079_
