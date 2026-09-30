# [?] Fix use-after-free in CTxMemPool::removeConflicts()

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2017-01-10
Source: https://github.com/dogecoin/dogecoin/commit/fe7e593b24678082578e76d8f918d4544713b5f0
Type: security-commit

## Details
Fix use-after-free in CTxMemPool::removeConflicts()

## Patch
### src/txmempool.cpp
```diff
@@ -581,8 +581,8 @@ void CTxMemPool::removeConflicts(const CTransaction &tx)
             const CTransaction &txConflict = *it->second;
             if (txConflict != tx)
             {
-                removeRecursive(txConflict);
                 ClearPrioritisation(txConflict.GetHash());
+                removeRecursive(txConflict);
             }
         }
     }
```
