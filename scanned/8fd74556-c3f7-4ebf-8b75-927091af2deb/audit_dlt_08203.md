# [?] Resolve race condition in remove dead accounts (#6984)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2025-07-16
Source: https://github.com/anza-xyz/agave/commit/7f30c4b277cb78609fc569f936c50e8c536e4314
Type: security-commit

## Details
Resolve race condition in remove dead accounts (#6984)

* Resolve race condition in remove_dead_accounts

## Patch
### accounts-db/src/accounts_db.rs
```diff
@@ -7212,14 +7212,13 @@ impl AccountsDb {
                     store.slot(),
                     *slot
                 );
-                if offsets.len() == store.count() {
+
+                let remaining_accounts = if offsets.len() == store.count() {
                     // all remaining alive accounts in the storage are being removed, so the entire storage/slot is dead
-                    store.remove_accounts(store.alive_bytes(), offsets.len());
-                    self.dirty_stores.insert(*slot, store);
-                    dead_slots.insert(*slot);
+                    store.remove_accounts(store.alive_bytes(), offsets.len())
                 } else {
                     // not all accounts are being removed, so figure out sizes of accounts we are removing and update the alive bytes and alive account count
-                    let (_, us) = measure_us!({
+                    let (remaining_accounts, us) = measure_us!({
                         let mut offsets = offsets.iter().cloned().collect::<Vec<_>>();
                         // sort so offsets are in order. This improves efficiency of loading the accounts.
                         offsets.sort_unstable();
@@ -7228,7 +7227,7 @@ impl AccountsDb {
                             .iter()
                             .map(|len| store.accounts.calculate_stored_size(*len))
                             .sum();
-                        store.remove_accounts(dead_bytes, offsets.len());
+                        let remaining_accounts = store.remove_accounts(dead_bytes, offsets.len());
 
                         if let MarkAccountsObsolete::Yes(slot_marked_obsolete) =
                             mark_accounts_obsolete
@@ -7238,21 +7237,29 @@ impl AccountsDb {
                                 slot_marked_obsolete,
                             );
                         }
-
-                        if Self::is_shrinking_productive(&store)
-                            && self.is_candidate_for_shrink(&store)
-                        {
-                            // Checking that this single storage entry is ready for shrinking,
-                            // should be a sufficient indication that the slot is ready to be shrunk
-                            // because slots should only have one storage entry, namely the one that was
-                            // created by `flush_slot_cache()`.
-                            new_shrink_candidates.insert(*slot);
-                        }
+                        remaining_accounts
                     });
                     self.clean_accounts_stats
                         .get_account_sizes_us
                         .fetch_add(us, Ordering::Relaxed);
-                }
+                    remaining_accounts
+                };
+
+                // Check if we have removed all accounts from the storage
+                // This may be different from the check above as this
+                // can be multithreaded
+                if remaining_accounts == 0 {
+                    self.dirty_stores.insert(*slot, store);
+                    dead_slots.insert(*slot);
+                } else if Self::is_shrinking_productive(&store)
+                    && self.is_candidate_for_shrink(&store)
+                {
+                    // Checking that this single storage entry is ready for shrinking,
+                    // should be a sufficient indication that the slot is ready to be shrunk
+                    // because slots should only have one storage entry, namely the one that was
+                    // created by `flush_slot_cache()`.
+                    new_shrink_candidates.insert(*slot);
+                };
             }
         });
         measure.stop();
```
