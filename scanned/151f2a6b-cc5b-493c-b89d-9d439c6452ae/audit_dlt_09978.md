# [?] Avoid signed integer overflow when loading a mempool.dat file with a malformed time field

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-11-11
Source: https://github.com/litecoin-project/litecoin/commit/ee11a412a537f62aa46e8862678ce2069a2df5b7
Type: security-commit

## Details
Avoid signed integer overflow when loading a mempool.dat file with a malformed time field

## Patch
### src/validation.cpp
```diff
@@ -5084,7 +5084,7 @@ bool LoadMempool(CTxMemPool& pool)
                 pool.PrioritiseTransaction(tx->GetHash(), amountdelta);
             }
             TxValidationState state;
-            if (nTime + nExpiryTimeout > nNow) {
+            if (nTime > nNow - nExpiryTimeout) {
                 LOCK(cs_main);
                 AcceptToMemoryPoolWithTime(chainparams, pool, state, tx, nTime,
                                            nullptr /* plTxnReplaced */, false /* bypass_limits */,
```
