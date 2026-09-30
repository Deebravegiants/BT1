# [?] Merge #7904: txdb: Fix assert crash in new UTXO set cursor

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-04-19
Source: https://github.com/dogecoin/dogecoin/commit/fc9e3346e6749585f701e9d1cb59e60f1d152d06
Type: security-commit

## Details
Merge #7904: txdb: Fix assert crash in new UTXO set cursor

a3310b4 txdb: Fix assert crash in new UTXO set cursor (Wladimir J. van der Laan)

## Patch
### src/txdb.cpp
```diff
@@ -134,12 +134,8 @@ bool CCoinsViewDBCursor::Valid() const
 void CCoinsViewDBCursor::Next()
 {
     pcursor->Next();
-    if (pcursor->Valid()) {
-        bool ok = pcursor->GetKey(keyTmp);
-        assert(ok); // If GetKey fails here something must be wrong with underlying database, we cannot handle that here
-    } else {
+    if (!pcursor->Valid() || !pcursor->GetKey(keyTmp))
         keyTmp.first = 0; // Invalidate cached key after last record so that Valid() and GetKey() return false
-    }
 }
 
 bool CBlockTreeDB::WriteBatchSync(const std::vector<std::pair<int, const CBlockFileInfo*> >& fileInfo, int nLastFile, const std::vector<const CBlockIndex*>& blockinfo) {
```
