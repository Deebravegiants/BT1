# [?] Fixing race condition identified by tsan.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-08-22
Source: https://github.com/nanocurrency/nano-node/commit/e58bd4239c949542d2d745c9f4c4145589eee547
Type: security-commit

## Details
Fixing race condition identified by tsan.

## Patch
### rai/node/node.cpp
```diff
@@ -2800,36 +2800,6 @@ int rai::node::store_version ()
 	return store.version_get (transaction);
 }
 
-rai::fan::fan (rai::uint256_union const & key, size_t count_a)
-{
-    std::unique_ptr <rai::uint256_union> first (new rai::uint256_union (key));
-    for (auto i (1); i < count_a; ++i)
-    {
-        std::unique_ptr <rai::uint256_union> entry (new rai::uint256_union);
-        random_pool.GenerateBlock (entry->bytes.data (), entry->bytes.size ());
-        *first ^= *entry;
-        values.push_back (std::move (entry));
-    }
-    values.push_back (std::move (first));
-}
-
-void rai::fan::value (rai::raw_key & prv_a)
-{
-    prv_a.data.clear ();
-    for (auto & i: values)
-    {
-        prv_a.data ^= *i;
-    }
-}
-
-void rai::fan::value_set (rai::raw_key const & value_a)
-{
-    rai::raw_key value_l;
-	value (value_l);
-    *(values [0]) ^= value_l.data;
-    *(values [0]) ^= value_a.data;
-}
-
 rai::thread_runner::thread_runner (boost::asio::io_service & service_a, unsigned service_threads_a)
 {
 	for (auto i (0); i < service_threads_a; ++i)
```

### rai/node/wallet.cpp
```diff
@@ -342,8 +342,7 @@ bool rai::wallet_store::rekey (MDB_txn * transaction_a, std::string const & pass
 		wallet_key (wallet_key_l, transaction_a);
         rai::raw_key password_l;
 		password.value (password_l);
-        (*password.values [0]) ^= password_l.data;
-        (*password.values [0]) ^= password_new.data;
+		password.value_set (password_new);
         rai::uint256_union encrypted;
 		encrypted.encrypt (wallet_key_l, password_new, salt (transaction_a).owords [0]);
 		entry_put_raw (transaction_a, rai::wallet_store::wallet_key_special, rai::wallet_value (encrypted));
@@ -361,6 +360,44 @@ void rai::wallet_store::derive_key (rai::raw_key & prv_a, MDB_txn * transaction_
 	kdf.phs (prv_a, password_a, salt_l);
 }
 
+rai::fan::fan (rai::uint256_union const & key, size_t count_a)
+{
+    std::unique_ptr <rai::uint256_union> first (new rai::uint256_union (key));
+    for (auto i (1); i < count_a; ++i)
+    {
+        std::unique_ptr <rai::uint256_union> entry (new rai::uint256_union);
+        random_pool.GenerateBlock (entry->bytes.data (), entry->bytes.size ());
+        *first ^= *entry;
+        values.push_back (std::move (entry));
+    }
+    values.push_back (std::move (first));
+}
+
+void rai::fan::value (rai::raw_key & prv_a)
+{
+	std::lock_guard <std::mutex> lock (mutex);
+	value_get (prv_a);
+}
+
+void rai::fan::value_get (rai::raw_key & prv_a)
+{
+	assert (!mutex.try_lock ());
+    prv_a.data.clear ();
+    for (auto & i: values)
+    {
+        prv_a.data ^= *i;
+    }
+}
+
+void rai::fan::value_set (rai::raw_key const & value_a)
+{
+	std::lock_guard <std::mutex> lock (mutex);
+    rai::raw_key value_l;
+	value_get (value_l);
+    *(values [0]) ^= value_l.data;
+    *(values [0]) ^= value_a.data;
+}
+
 rai::wallet_value::wallet_value (MDB_val const & val_a)
 {
 	assert (val_a.mv_size == sizeof (*this));
```

### rai/node/wallet.hpp
```diff
@@ -49,6 +49,9 @@ class fan
     void value (rai::raw_key &);
     void value_set (rai::raw_key const &);
     std::vector <std::unique_ptr <rai::uint256_union>> values;
+private:
+	std::mutex mutex;
+	void value_get (rai::raw_key &);
 };
 class wallet_value
 {
```
