# [?] Fixing slow_test store.pruned_load. This was crashing on the line store->pruned.del as hashes was empty and querying for .begin (). hashes was never p

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2022-01-11
Source: https://github.com/nanocurrency/nano-node/commit/943e9e69ca4798340a83b0a97ced527d6992234e
Type: security-commit

## Details
Fixing slow_test store.pruned_load. This was crashing on the line store->pruned.del as hashes was empty and querying for .begin (). hashes was never populated even when this test was originally added.

## Patch
### nano/slow_test/node.cpp
```diff
@@ -443,12 +443,13 @@ TEST (store, pruned_load)
 					nano::block_hash random_hash;
 					nano::random_pool::generate_block (random_hash.bytes.data (), random_hash.bytes.size ());
 					store->pruned.put (transaction, random_hash);
+					hashes.insert (random_hash);
 				}
 			}
 			if (!nano::rocksdb_config::using_rocksdb_in_tests ())
 			{
 				auto transaction (store->tx_begin_write ());
-				for (auto k (0); k < batch_size / 2; ++k)
+				for (auto k (0); !hashes.empty () && k < batch_size / 2; ++k)
 				{
 					auto hash (hashes.begin ());
 					store->pruned.del (transaction, *hash);
```
