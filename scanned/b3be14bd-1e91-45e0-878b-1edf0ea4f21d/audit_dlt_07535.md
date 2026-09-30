# [?] Fix race condition in unchecked_map where a block may be asynchronously inserted and a dependency satisfied while a block is waiting to be placed in t

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2023-01-31
Source: https://github.com/nanocurrency/nano-node/commit/a1e359bae7a53de665c03b189a0ed9b6865689a6
Type: security-commit

## Details
Fix race condition in unchecked_map where a block may be asynchronously inserted and a dependency satisfied while a block is waiting to be placed in the unchecked table.

This change checks if the dependency has been satisfied before placing it in the unchecked map.

## Patch
### nano/node/unchecked_map.cpp
```diff
@@ -209,6 +209,12 @@ void nano::unchecked_map::run ()
 
 void nano::unchecked_map::insert_impl (nano::write_transaction const & transaction, nano::hash_or_account const & dependency, nano::unchecked_info const & info)
 {
+	// Check if block dependency has been satisfied while waiting to be placed in the unchecked map
+	if (store.block.exists (transaction, dependency.as_block_hash ()))
+	{
+		satisfied (info);
+		return;
+	}
 	nano::lock_guard<std::recursive_mutex> lock{ entries_mutex };
 	// Check if we should be using memory but the memory container hasn't been constructed i.e. we're transitioning from disk to memory.
 	if (entries == nullptr && use_memory ())
@@ -221,7 +227,7 @@ void nano::unchecked_map::insert_impl (nano::write_transaction const & transacti
 	}
 	if (entries == nullptr)
 	{
-		store.unchecked.put (transaction, dependency, { info.block });
+		store.unchecked.put (transaction, dependency, info);
 	}
 	else
 	{
```
