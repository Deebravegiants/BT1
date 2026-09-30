# [?] Cache tx Trust per-call to avoid DoS

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2019-08-30
Source: https://github.com/litecoin-project/litecoin/commit/595f09d6de7f1b94428cdd1310777aa6a4c584e5
Type: security-commit

## Details
Cache tx Trust per-call to avoid DoS

## Patch
### src/wallet/wallet.cpp
```diff
@@ -2294,6 +2294,12 @@ bool CWalletTx::InMempool() const
 }
 
 bool CWalletTx::IsTrusted(interfaces::Chain::Lock& locked_chain) const
+{
+    std::set<uint256> s;
+    return IsTrusted(locked_chain, s);
+}
+
+bool CWalletTx::IsTrusted(interfaces::Chain::Lock& locked_chain, std::set<uint256>& trustedParents) const
 {
     // Quick answer in most cases
     if (!locked_chain.checkFinalTx(*tx)) {
@@ -2322,9 +2328,13 @@ bool CWalletTx::IsTrusted(interfaces::Chain::Lock& locked_chain) const
         // Check that this specific input being spent is trusted
         if (pwallet->IsMine(parentOut) != ISMINE_SPENDABLE)
             return false;
+        // If we've already trusted this parent, continue
+        if (trustedParents.count(parent->GetHash()))
+            continue;
         // Recurse to check that the parent is also trusted
-        if (!parent->IsTrusted(locked_chain))
+        if (!parent->IsTrusted(locked_chain, trustedParents))
             return false;
+        trustedParents.insert(parent->GetHash());
     }
     return true;
 }
```

### src/wallet/wallet.h
```diff
@@ -616,6 +616,7 @@ class CWalletTx
 
     bool InMempool() const;
     bool IsTrusted(interfaces::Chain::Lock& locked_chain) const;
+    bool IsTrusted(interfaces::Chain::Lock& locked_chain, std::set<uint256>& trustedParents) const;
 
     int64_t GetTxTime() const;
 
```
