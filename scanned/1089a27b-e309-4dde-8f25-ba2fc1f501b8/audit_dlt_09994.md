# [?] Fix possible race condition in eth-call: catch error caused by version invalidated mid run

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2025-08-27
Source: https://github.com/category-labs/monad/commit/3de49a0a98691d0c79a7ae944ca036ee31135ec2
Type: security-commit

## Details
Fix possible race condition in eth-call: catch error caused by version invalidated mid run

## Patch
### category/execution/ethereum/db/trie_rodb.hpp
```diff
@@ -20,6 +20,7 @@
 #include <category/execution/ethereum/db/db.hpp>
 #include <category/execution/ethereum/db/util.hpp>
 #include <category/mpt/db.hpp>
+#include <category/mpt/db_error.hpp>
 #include <category/vm/vm.hpp>
 
 #include <evmc/hex.hpp>
@@ -52,12 +53,18 @@ class TrieRODb final : public ::monad::Db
         auto const prefix = block_id == bytes32_t{} ? finalized_nibbles
                                                     : proposal_prefix(block_id);
         auto res = db_.find(prefix, block_number);
-        // TODO: error handling instead of assert
-        MONAD_ASSERT_PRINTF(
-            res.has_value(),
-            "block %lu, block_id %s",
-            block_number,
-            evmc::hex(to_byte_string_view(block_id.bytes)).c_str());
+        if (res.has_error()) {
+            MONAD_ASSERT_PRINTF(
+                res.assume_error() ==
+                    ::monad::mpt::DbError::version_no_longer_exist,
+                "Cannot find block_id %s prefix at block %lu where block is "
+                "still valid in db",
+                evmc::hex(to_byte_string_view(block_id.bytes)).c_str(),
+                block_number);
+            MONAD_THROW(
+                "Block was invalidated in db while execution was in progress",
+                res.has_value());
+        }
         prefix_cursor_ = res.value();
         block_number_ = block_number;
     }
@@ -71,6 +78,10 @@ class TrieRODb final : public ::monad::Db
                 mpt::NibblesView{keccak256({addr.bytes, sizeof(addr.bytes)})}),
             block_number_);
         if (!acc_leaf_res.has_value()) {
+            MONAD_THROW(
+                "Block was invalidated in db while execution was in progress",
+                acc_leaf_res.assume_error() !=
+                    ::monad::mpt::DbError::version_no_longer_exist);
             return std::nullopt;
         }
         auto encoded_account = acc_leaf_res.value().node->value();
@@ -90,6 +101,10 @@ class TrieRODb final : public ::monad::Db
                 mpt::NibblesView{keccak256({key.bytes, sizeof(key.bytes)})}),
             block_number_);
         if (!storage_leaf_res.has_value()) {
+            MONAD_THROW(
+                "Block was invalidated in db while execution was in progress",
+                storage_leaf_res.assume_error() !=
+                    ::monad::mpt::DbError::version_no_longer_exist);
             return {};
         }
         auto encoded_storage = storage_leaf_res.value().node->value();
@@ -108,6 +123,10 @@ class TrieRODb final : public ::monad::Db
                 mpt::NibblesView{to_byte_string_view(code_hash.bytes)}),
             block_number_);
         if (!code_leaf_res.has_value()) {
+            MONAD_THROW(
+                "Block was invalidated in db while execution was in progress",
+                code_leaf_res.assume_error() !=
+                    ::monad::mpt::DbError::version_no_longer_exist);
             return vm::make_shared_intercode({});
         }
         return vm::make_shared_intercode(code_leaf_res.value().node->value());
```
