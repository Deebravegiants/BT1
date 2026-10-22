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

ACKs for top commit:
  PastaPastaPasta:
    utACK e8ec63a1e090f4e6bcdfa3cd48891c8672b51433
  UdjinM6:
    utACK e8ec63a1e090f4e6bcdfa3cd48891c8672b51433
  PastaPastaPasta:
    utACK e8ec63a1e090f4e6bcdfa3cd48891c8672b51433

Tree-SHA512: 92f2f2abe0b3dd837c45cdb8d25e65454083fac0be268252f93b477c4355b91095b45393efc05561cbdf6e46e9d68b4c9c60d2255c6ac7a679905e9e3f0c55fb

### src/coinjoin/coinjoin.cpp
```diff
@@ -57,6 +57,7 @@ bool CCoinJoinQueue::CheckSignature(const CBLSPublicKey& blsPubKey) const
 
 bool CCoinJoinQueue::IsTimeOutOfBounds(int64_t current_time) const
 {
+    if (current_time < 0 || nTime < 0) return true;
     return current_time - nTime > COINJOIN_QUEUE_TIMEOUT ||
            nTime - current_time > COINJOIN_QUEUE_TIMEOUT;
 }
```

### src/coinjoin/common.h
```diff
@@ -118,6 +118,7 @@ constexpr bool IsCollateralAmount(CAmount nInputAmount)
 
 constexpr int CalculateAmountPriority(CAmount nInputAmount)
 {
+    if (nInputAmount < 0 || nInputAmount > MAX_MONEY) return 0;
     if (auto optDenom = util::find_if_opt(GetStandardDenominations(),
                                           [&nInputAmount](const auto& denom) { return nInputAmount == denom; })) {
         return (float)COIN / *optDenom * 10000;
```

### src/test/coinjoin_queue_tests.cpp
```diff
@@ -7,9 +7,14 @@
 #include <active/masternode.h>
 #include <bls/bls.h>
 #include <coinjoin/coinjoin.h>
+#include <coinjoin/common.h>
+#include <consensus/amount.h>
 
 #include <uint256.h>
 
+#include <climits>
+#include <cstdint>
+
 #include <boost/test/unit_test.hpp>
 
 BOOST_FIXTURE_TEST_SUITE(coinjoin_queue_tests, TestingSetup)
@@ -96,4 +101,48 @@ BOOST_AUTO_TEST_CASE(queue_timestamp_validation)
     BOOST_CHECK(q.IsTimeOutOfBounds(current_time));
 }
 
+BOOST_AUTO_TEST_CASE(queue_timestamp_extreme_values)
+{
+    CCoinJoinQueue q;
+    q.nDenom = CoinJoin::AmountToDenomination(CoinJoin::GetSmallestDenomination());
+    q.m_protxHash = uint256::ONE;
+
+    // Negative timestamps are rejected by the guard
+    q.nTime = INT64_MIN;
+    BOOST_CHECK(q.IsTimeOutOfBounds(INT64_MAX));
+
+    q.nTime = INT64_MAX;
+    BOOST_CHECK(q.IsTimeOutOfBounds(INT64_MIN));
+
+    q.nTime = INT64_MIN;
+    BOOST_CHECK(q.IsTimeOutOfBounds(INT64_MIN));
+
+    // Large positive timestamp with same value: zero diff, in bounds
+    q.nTime = INT64_MAX;
+    BOOST_CHECK(!q.IsTimeOutOfBounds(INT64_MAX));
+
+    // Zero vs extreme positive: huge gap, out of bounds
+    q.nTime = 0;
+    BOOST_CHECK(q.IsTimeOutOfBounds(INT64_MAX));
+
+    // Zero vs negative: rejected by guard
+    q.nTime = 0;
+    BOOST_CHECK(q.IsTimeOutOfBounds(INT64_MIN));
+}
+
+static_assert(CoinJoin::CalculateAmountPriority(MAX_MONEY) == -(MAX_MONEY / COIN));
+static_assert(CoinJoin::CalculateAmountPriority(static_cast<CAmount>(INT64_MAX)) == 0);
+static_assert(CoinJoin::CalculateAmountPriority(static_cast<CAmount>(-1)) == 0);
+
+BOOST_AUTO_TEST_CASE(calculate_amount_priority_guard)
+{
+    // Realistic amount: MAX_MONEY (21 million DASH)
+    BOOST_CHECK_EQUAL(CoinJoin::CalculateAmountPriority(MAX_MONEY), -(MAX_MONEY / COIN));
+
+    // Out-of-range amounts return 0
+    BOOST_CHECK_EQUAL(CoinJoin::CalculateAmountPriority(static_cast<CAmount>(INT64_MAX)), 0);
+    BOOST_CHECK_EQUAL(CoinJoin::CalculateAmountPriority(static_cast<CAmount>(-1)), 0);
+    BOOST_CHECK_EQUAL(CoinJoin::CalculateAmountPriority(MAX_MONEY + 1), 0);
+}
+
 BOOST_AUTO_TEST_SUITE_END()
```
