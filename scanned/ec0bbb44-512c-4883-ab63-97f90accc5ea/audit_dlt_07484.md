# [?] txdb: Fix assert crash in new UTXO set cursor

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-04-18
Source: https://github.com/dogecoin/dogecoin/commit/a3310b4d485b1510c240f1db882530590b6fd7c9
Type: security-commit

## Details
txdb: Fix assert crash in new UTXO set cursor

Remove the mistaken assumption that GetKey returning false signifies
an internal database issue. It will return false when the key cannot
be deserialized into the (char,uint256) stanza, which indicates
that the cursor has reached a different kind of key.

Fixes bug #7890 introduced in #7756.

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
