# [?] handle ancient overflow case correctly (#29458)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-01-02
Source: https://github.com/solana-labs/solana/commit/e99afb4e8540cffdf1efa961a9e03c247890683b
Type: security-commit

## Details
handle ancient overflow case correctly (#29458)

## Patch
### runtime/src/accounts_db.rs
```diff
@@ -4501,7 +4501,8 @@ impl AccountsDb {
             return; // skipping slot with no useful accounts to write
         }
 
-        let (shrink_in_progress, time) = measure!(current_ancient.create_if_necessary(slot, self));
+        let (mut shrink_in_progress, time) =
+            measure!(current_ancient.create_if_necessary(slot, self));
         let mut create_and_insert_store_elapsed_us = time.as_us();
         let available_bytes = current_ancient.append_vec().accounts.remaining_bytes();
         // split accounts in 'slot' into:
@@ -4532,8 +4533,17 @@ impl AccountsDb {
             // Assert: it cannot be the case that we already had an ancient append vec at this slot and
             // yet that ancient append vec does not have room for the accounts stored at this slot currently
             assert_ne!(slot, current_ancient.slot());
-            let (_, time) = measure!(current_ancient.create_ancient_append_vec(slot, self));
+            let (shrink_in_progress_overflow, time) =
+                measure!(current_ancient.create_ancient_append_vec(slot, self));
             create_and_insert_store_elapsed_us += time.as_us();
+            // We cannot possibly be shrinking the original slot that created an ancient append vec
+            // AND not have enough room in the ancient append vec at that slot
+            // to hold all the contents of that slot.
+            // We need this new 'shrink_in_progress' to be used in 'remove_old_stores_shrink' below.
+            // All non-overflow accounts were put in a prior slot's ancient append vec. All overflow accounts
+            // are essentially being shrunk into a new ancient append vec in 'slot'.
+            assert!(shrink_in_progress.is_none());
+            shrink_in_progress = Some(shrink_in_progress_overflow);
 
             // write the overflow accounts to the next ancient storage
             let timing =
```
