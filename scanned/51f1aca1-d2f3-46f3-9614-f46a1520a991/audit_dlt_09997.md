# [?] fix db_test byte_string_view use-after-free asan error

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2025-02-04
Source: https://github.com/category-labs/monad/commit/a1f84bbe2342b9536193fdd5dc37f71ce1e6730a
Type: security-commit

## Details
fix db_test byte_string_view use-after-free asan error

rename some EXPECT_TRUE -> ASSERT_TRUE

## Patch
### libs/db/src/monad/mpt/db.hpp
```diff
@@ -49,8 +49,14 @@ class Db
     Db &operator=(Db &&) = delete;
     ~Db();
 
-    // May wait on a fiber future
-    //  The `block_id` parameter is used for version control validation
+    // The find, get, and get_data API calls return non-owning references.
+    // The result lifetime ends when a subsequent operation reloads the trie
+    // root. This can happen due to an RWDb upsert, an RODb reading a different
+    // version, or an RODb reading the same version that has been updated by an
+    // RWDb in another process.
+    // The `block_id` parameter specify the version to read from, and is also
+    // used for version control validation. These calls may wait on a fiber
+    // future.
     Result<NodeCursor> find(NodeCursor, NibblesView, uint64_t block_id) const;
     Result<NodeCursor> find(NibblesView prefix, uint64_t block_id) const;
     Result<byte_string_view> get(NibblesView, uint64_t block_id) const;
```

### libs/db/src/monad/mpt/test/db_test.cpp
```diff
@@ -1114,12 +1114,13 @@ TEST(DbTest, out_of_order_upserts_with_compaction)
             continue;
         }
         auto const result_n = rodb.get({}, block_id);
-        EXPECT_TRUE(result_n.has_value());
+        ASSERT_TRUE(result_n.has_value());
         auto const [fast_n, slow_n] = get_release_offsets(result_n.value());
-        auto const result_before = rodb.get({}, block_id - 1);
-        EXPECT_TRUE(result_before.has_value());
-        auto const [fast_n_1, slow_n_1] =
-            get_release_offsets(result_before.value());
+        monad::Result<monad::byte_string_view> const res =
+            rodb.get({}, block_id - 1);
+        ASSERT_TRUE(res.has_value());
+        monad::byte_string const result_before{res.value()};
+        auto const [fast_n_1, slow_n_1] = get_release_offsets(result_before);
         EXPECT_GE(fast_n, fast_n_1);
         EXPECT_GE(slow_n, slow_n_1);
         // upsert on top of N-1
@@ -1133,9 +1134,9 @@ TEST(DbTest, out_of_order_upserts_with_compaction)
             make_update(kv_alloc[3], kv_alloc[3]),
             make_update(kv_alloc[4], kv_alloc[4]));
         auto const result_after = rodb.get({}, block_id - 1);
-        EXPECT_TRUE(result_after.has_value());
+        ASSERT_TRUE(result_after.has_value());
         // offsets remain the same after the second upsert
-        EXPECT_EQ(result_before.value(), result_after.value());
+        EXPECT_EQ(result_before, result_after.value());
         // convert to byte_string so that both data are in scope
         monad::byte_string const data_n_1{
             rodb.get_data({prefix}, block_id - 1).value()};
@@ -1148,7 +1149,7 @@ TEST(DbTest, out_of_order_upserts_with_compaction)
 
     ASSERT_EQ(n, block_id * keys_per_version);
     auto const result_n = rodb.get({}, block_id - 1);
-    EXPECT_TRUE(result_n.has_value());
+    ASSERT_TRUE(result_n.has_value());
     auto const [fast_n, slow_n] = get_release_offsets(result_n.value());
     EXPECT_EQ(
         rodb.get_data({prefix}, block_id - 1).value(),
@@ -1535,7 +1536,7 @@ TEST_F(OnDiskDbFixture, rw_query_old_version)
     // This will exceed the ring buffer capacity, kicking out the first write.
     write(kv[1].first, kv[1].second, block_id + i);
     auto bad_read = this->db.get(prefix + kv[0].first, block_id);
-    EXPECT_TRUE(bad_read.has_error());
+    ASSERT_TRUE(bad_read.has_error());
     EXPECT_EQ(bad_read.error(), DbError::key_not_found);
 }
 
@@ -1964,7 +1965,7 @@ TEST_F(OnDiskDbWithFileFixture, reset_history_length_concurrent)
     EXPECT_EQ(ro_db.get_history_length(), DBTEST_HISTORY_LENGTH);
     EXPECT_EQ(ro_db.get_latest_block_id(), DBTEST_HISTORY_LENGTH - 1);
     auto const res = ro_db.get(prefix + kv[0].first, 0);
-    EXPECT_TRUE(res.has_value());
+    ASSERT_TRUE(res.has_value());
     EXPECT_EQ(res.value(), kv[0].second);
 
     uint64_t const end_history_length =
```
