# [?] Fix potential crash

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-11-29
Source: https://github.com/Zilliqa/zq1/commit/0d1854424a419321cfda3a480dce3f3845723156
Type: security-commit

## Details
Fix potential crash

## Patch
### src/libNetwork/RumorManager.cpp
```diff
@@ -365,7 +365,7 @@ bool RumorManager::RumorReceived(uint8_t type, int32_t round,
       hash = HashUtils::BytesToHash(message);
 
       auto it1 = m_rumorIdHashBimap.right.find(message);
-      if (it1 == m_rumorIdHashBimap.right.end()) {
+      if (it1 != m_rumorIdHashBimap.right.end()) {
         recvdRumorId = it1->second;
       }
 
```
