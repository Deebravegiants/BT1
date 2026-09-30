# [?] CAP-38: Fix integer overflow in exchangeWithPool

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2021-09-08
Source: https://github.com/stellar/stellar-core/commit/f156b80835da53fd8beb753c65eb2a43735de522
Type: security-commit

## Details
CAP-38: Fix integer overflow in exchangeWithPool

## Patch
### src/transactions/OfferExchange.cpp
```diff
@@ -1248,6 +1248,19 @@ exchangeWithPool(int64_t reservesToPool, int64_t maxSendToPool, int64_t& toPool,
     {
     case RoundingType::PATH_PAYMENT_STRICT_SEND:
     {
+        // PathPaymentStrictSend always allows INT64_MAX to be received at
+        // every hop, and exchange with a pool always happens as a unit
+        // (compare against the order book where multiple offers might execute
+        // in a hop).
+        if (maxReceiveFromPool != INT64_MAX)
+        {
+            throw std::runtime_error("strict send with bounded receive?");
+        }
+        // We can't receive more from the pool then it has reserves.
+        maxReceiveFromPool = reservesFromPool;
+
+        // We have to send this amount exactly, and we can't do it if that would
+        // overflow reserves.
         if (maxSendToPool > INT64_MAX - reservesToPool)
         {
             return false;
@@ -1259,14 +1272,26 @@ exchangeWithPool(int64_t reservesToPool, int64_t maxSendToPool, int64_t& toPool,
         bool res = hugeDivide(fromPool, maxBps - feeBps,
                               bigMultiply(reservesFromPool, toPool),
                               denominator, ROUND_DOWN);
-        if (res)
-        {
-            fromPool = std::min(fromPool, maxReceiveFromPool);
-        }
-        return res;
+
+        // Fail if the division overflows, or if we would be receiving too much
+        // from the pool.
+        return res && fromPool <= maxReceiveFromPool;
     }
     case RoundingType::PATH_PAYMENT_STRICT_RECEIVE:
     {
+        // PathPaymentStrictReceive always allows INT64_MAX to be sent at every
+        // hop, and exchange with a pool always happens as a unit (compare
+        // against the order book where multiple offers might execute in a hop).
+        if (maxSendToPool != INT64_MAX)
+        {
+            throw std::runtime_error("strict receive with bounded send?");
+        }
+        // We can't send more to the pool then it has space for additional
+        // reserves.
+        maxSendToPool = INT64_MAX - reservesToPool;
+
+        // We have to receive this amount exactly, and we can't do it if that
+        // would deplete reserves entirely.
         if (maxReceiveFromPool >= reservesFromPool)
         {
             return false;
@@ -1277,11 +1302,10 @@ exchangeWithPool(int64_t reservesToPool, int64_t maxSendToPool, int64_t& toPool,
             toPool, maxBps, bigMultiply(reservesToPool, fromPool),
             bigMultiply(reservesFromPool - fromPool, maxBps - feeBps),
             ROUND_UP);
-        if (res)
-        {
-            toPool = std::min(toPool, maxSendToPool);
-        }
-        return res;
+
+        // Fail if the division overflows, or if we would be sending too much to
+        // the pool.
+        return res && toPool <= maxSendToPool;
     }
     default:
         throw std::runtime_error("Invalid rounding type");
```
