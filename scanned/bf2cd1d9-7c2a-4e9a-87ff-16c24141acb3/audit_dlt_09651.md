# [?] Merge #9507: Fix use-after-free in CTxMemPool::removeConflicts()

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2017-01-11
Source: https://github.com/dogecoin/dogecoin/commit/05950427d310654774031764a7141a1a4fd9c6e4
Type: security-commit

## Details
Merge #9507: Fix use-after-free in CTxMemPool::removeConflicts()

fe7e593 Fix use-after-free in CTxMemPool::removeConflicts() (Suhas Daftuar)

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
