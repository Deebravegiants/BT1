# [?] Fix node crashed when calculate extra micro block info hash

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-11-07
Source: https://github.com/Zilliqa/zq1/commit/5e4024557efd4590931be6af532945cb2c291a1a
Type: security-commit

## Details
Fix node crashed when calculate extra micro block info hash

## Patch
### src/libMessage/Messenger.cpp
```diff
@@ -2108,6 +2108,13 @@ bool Messenger::GetExtraMbInfoHash(const std::vector<bool>& isMicroBlockEmpty,
     return false;
   }
 
+  // Fix software crash because of tmp is empty triggered assertion in
+  // sha2.update.git
+  if (tmp.empty()) {
+    LOG_GENERAL(WARNING, "ProtoExtraMbInfo is empty, proceed without it.");
+    return true;
+  }
+
   SHA2<HASH_TYPE::HASH_VARIANT_256> sha2;
   sha2.Update(tmp);
   tmp = sha2.Finalize();
```
