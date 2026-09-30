# [?] Fix DoS vulnerability in mempool acceptance

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-07-07
Source: https://github.com/dogecoin/dogecoin/commit/bb66a11396335b5f4e5914806fcb2dc6165edf6f
Type: security-commit

## Details
Fix DoS vulnerability in mempool acceptance

Moves the IsStandard check to happen after the premature-witness check,
so that adding a witness to a transaction can't prevent mempool acceptance.

Note that this doesn't address the broader category of potential mempool DoS
issues that affect transactions after segwit activation.

## Patch
### src/main.cpp
```diff
@@ -1132,11 +1132,6 @@ bool AcceptToMemoryPoolWorker(CTxMemPool& pool, CValidationState& state, const C
     if (tx.IsCoinBase())
         return state.DoS(100, false, REJECT_INVALID, "coinbase");
 
-    // Rather not work on nonstandard transactions (unless -testnet/-regtest)
-    string reason;
-    if (fRequireStandard && !IsStandardTx(tx, reason))
-        return state.DoS(0, false, REJECT_NONSTANDARD, reason);
-
     // Don't relay version 2 transactions until CSV is active, and we can be
     // sure that such transactions will be mined (unless we're on
     // -testnet/-regtest).
@@ -1150,6 +1145,11 @@ bool AcceptToMemoryPoolWorker(CTxMemPool& pool, CValidationState& state, const C
         return state.DoS(0, false, REJECT_NONSTANDARD, "no-witness-yet", true);
     }
 
+    // Rather not work on nonstandard transactions (unless -testnet/-regtest)
+    string reason;
+    if (fRequireStandard && !IsStandardTx(tx, reason))
+        return state.DoS(0, false, REJECT_NONSTANDARD, reason);
+
     // Only accept nLockTime-using transactions that can be mined in the next
     // block; we don't want our mempool filled up with transactions that can't
     // be mined yet.
```
