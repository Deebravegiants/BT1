# [?] fix crash when changing a partition log level with the wrong case

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2020-12-18
Source: https://github.com/stellar/stellar-core/commit/f6ab9ecf57cba0e604e4d22d0d276b2dda4e3861
Type: security-commit

## Details
fix crash when changing a partition log level with the wrong case

## Patch
### src/util/Logging.cpp
```diff
@@ -305,7 +305,14 @@ Logging::rotate()
 std::string
 Logging::normalizePartition(std::string const& partition)
 {
-    return partition;
+    for (auto& p : kPartitionNames)
+    {
+        if (iequals(partition, p))
+        {
+            return p;
+        }
+    }
+    throw std::invalid_argument("not a valid partition");
 }
 
 std::recursive_mutex Logging::mLogMutex;
```
