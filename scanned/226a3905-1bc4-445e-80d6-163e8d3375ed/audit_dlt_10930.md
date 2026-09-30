# [?] Fix deadlock

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-01-26
Source: https://github.com/Zilliqa/zq1/commit/44470aa40dcfd9fde4a04f61091dd3b9b6f1504f
Type: security-commit

## Details
Fix deadlock

## Patch
### src/libPersistence/ContractStorage.cpp
```diff
@@ -116,44 +116,46 @@ bool ContractStorage::PutContractState(
     dev::h256& stateHash, bool temp, bool revertible,
     const vector<Index>& existing_indexes, bool provideExisting) {
   // LOG_MARKER();
-  unique_lock<shared_timed_mutex> g(m_stateMainMutex);
+  {
+    unique_lock<shared_timed_mutex> g(m_stateMainMutex);
 
-  if (address == Address()) {
-    LOG_GENERAL(WARNING, "Null address rejected");
-    return false;
-  }
+    if (address == Address()) {
+      LOG_GENERAL(WARNING, "Null address rejected");
+      return false;
+    }
 
-  vector<Index> entry_indexes;
+    vector<Index> entry_indexes;
 
-  if (provideExisting) {
-    entry_indexes = existing_indexes;
-  } else {
-    entry_indexes = GetContractStateIndexes(address, temp);
-  }
+    if (provideExisting) {
+      entry_indexes = existing_indexes;
+    } else {
+      entry_indexes = GetContractStateIndexes(address, temp);
+    }
 
-  unordered_map<string, string> batch;
+    unordered_map<string, string> batch;
 
-  for (const auto& entry : entries) {
-    // Append the new index to the existing indexes
-    if (find(entry_indexes.begin(), entry_indexes.end(), entry.first) ==
-        entry_indexes.end()) {
-      entry_indexes.emplace_back(entry.first);
-    }
+    for (const auto& entry : entries) {
+      // Append the new index to the existing indexes
+      if (find(entry_indexes.begin(), entry_indexes.end(), entry.first) ==
+          entry_indexes.end()) {
+        entry_indexes.emplace_back(entry.first);
+      }
 
-    if (temp) {
-      t_stateDataMap[entry.first.hex()] = entry.second;
-    } else {
-      if (revertible) {
-        r_stateDataMap[entry.first.hex()] = m_stateDataMap[entry.first.hex()];
+      if (temp) {
+        t_stateDataMap[entry.first.hex()] = entry.second;
+      } else {
+        if (revertible) {
+          r_stateDataMap[entry.first.hex()] = m_stateDataMap[entry.first.hex()];
+        }
+        m_stateDataMap[entry.first.hex()] = entry.second;
       }
-      m_stateDataMap[entry.first.hex()] = entry.second;
     }
-  }
 
-  // Update the stateIndexDB
-  if (!SetContractStateIndexes(address, entry_indexes, temp, revertible)) {
-    LOG_GENERAL(WARNING, "SetContractStateIndex failed");
-    return false;
+    // Update the stateIndexDB
+    if (!SetContractStateIndexes(address, entry_indexes, temp, revertible)) {
+      LOG_GENERAL(WARNING, "SetContractStateIndex failed");
+      return false;
+    }
   }
 
   stateHash = GetContractStateHash(address, temp);
```
