# [?] LMDB: fix deadlock in resized detection

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-09-19
Source: https://github.com/monero-project/monero/commit/5f54dea4ec36bd2f7c2fab1ded7d20c7a07ff8f9
Type: security-commit

## Details
LMDB: fix deadlock in resized detection

## Patch
### src/blockchain_db/lmdb/db_lmdb.cpp
```diff
@@ -467,7 +467,12 @@ void mdb_txn_safe::allow_new_txns()
   creation_gate.clear();
 }
 
-void lmdb_resized(MDB_env *env)
+void mdb_txn_safe::increment_txns(int i)
+{
+	num_active_txns += i;
+}
+
+void lmdb_resized(MDB_env *env, int isactive)
 {
   mdb_txn_safe::prevent_new_txns();
 
@@ -478,7 +483,11 @@ void lmdb_resized(MDB_env *env)
   mdb_env_info(env, &mei);
   uint64_t old = mei.me_mapsize;
 
+  if (isactive)
+    mdb_txn_safe::increment_txns(-1);
   mdb_txn_safe::wait_no_active_txns();
+  if (isactive)
+    mdb_txn_safe::increment_txns(1);
 
   int result = mdb_env_set_mapsize(env, 0);
   if (result)
@@ -496,7 +505,7 @@ inline int lmdb_txn_begin(MDB_env *env, MDB_txn *parent, unsigned int flags, MDB
 {
   int res = mdb_txn_begin(env, parent, flags, txn);
   if (res == MDB_MAP_RESIZED) {
-    lmdb_resized(env);
+    lmdb_resized(env, 1);
     res = mdb_txn_begin(env, parent, flags, txn);
   }
   return res;
@@ -506,7 +515,7 @@ inline int lmdb_txn_renew(MDB_txn *txn)
 {
   int res = mdb_txn_renew(txn);
   if (res == MDB_MAP_RESIZED) {
-    lmdb_resized(mdb_txn_env(txn));
+    lmdb_resized(mdb_txn_env(txn), 0);
     res = mdb_txn_renew(txn);
   }
   return res;
```

### src/blockchain_db/lmdb/db_lmdb.h
```diff
@@ -154,6 +154,7 @@ struct mdb_txn_safe
   static void prevent_new_txns();
   static void wait_no_active_txns();
   static void allow_new_txns();
+  static void increment_txns(int);
 
   mdb_threadinfo* m_tinfo;
   MDB_txn* m_txn;
```
