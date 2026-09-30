# [?] CAP-38: Use addBalance in exchangeWithPool to harden against overflow

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2021-09-09
Source: https://github.com/stellar/stellar-core/commit/ce245de87929b314f51c22ed031513e1e3e1784c
Type: security-commit

## Details
CAP-38: Use addBalance in exchangeWithPool to harden against overflow

## Patch
### src/transactions/OfferExchange.cpp
```diff
@@ -1392,8 +1392,11 @@ exchangeWithPool(AbstractLedgerTxn& ltxOuter, Asset const& toPoolAsset,
                                feeBps, round);
         if (res)
         {
-            cp().reserveA += toPool;
-            cp().reserveB -= fromPool;
+            if (!addBalance(cp().reserveA, toPool) ||
+                !addBalance(cp().reserveB, -fromPool))
+            {
+                throw std::runtime_error("could not update reserves");
+            }
         }
     }
     else if (fromPoolAsset == cp().params.assetA &&
@@ -1404,8 +1407,11 @@ exchangeWithPool(AbstractLedgerTxn& ltxOuter, Asset const& toPoolAsset,
                                feeBps, round);
         if (res)
         {
-            cp().reserveA -= fromPool;
-            cp().reserveB += toPool;
+            if (!addBalance(cp().reserveA, -fromPool) ||
+                !addBalance(cp().reserveB, toPool))
+            {
+                throw std::runtime_error("could not update reserves");
+            }
         }
     }
     else
```
