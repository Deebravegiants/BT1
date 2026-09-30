# [?] Fix a corner-case panic in get_entries_in_data_block() (#27195)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2022-08-18
Source: https://github.com/solana-labs/solana/commit/6d12bb6ec36dee3d46e0b530d7de6ca6d802a443
Type: security-commit

## Details
Fix a corner-case panic in get_entries_in_data_block() (#27195)

#### Problem
get_entries_in_data_block() panics when there's inconsistency between
slot_meta and data_shred.

However, as we don't lock on reads, reading across multiple column families is
not atomic (especially for older slots) and thus does not guarantee consistency
as the background cleanup service could purge the slot in the middle.  Such
panic was reported in #26980 when the validator serves a high load of RPC calls.

#### Summary of Changes
This PR makes get_entries_in_data_block() panic only when the inconsistency
between slot-meta and data-shred happens on a slot older than lowest_cleanup_slot.

## Patch
### ledger/src/blockstore.rs
```diff
@@ -2872,28 +2872,29 @@ impl Blockstore {
                     .and_then(|serialized_shred| {
                         if serialized_shred.is_none() {
                             if let Some(slot_meta) = slot_meta {
-                                panic!(
-                                    "Shred with
-                                    slot: {},
-                                    index: {},
-                                    consumed: {},
-                                    completed_indexes: {:?}
-                                    must exist if shred index was included in a range: {} {}",
-                                    slot,
-                                    i,
-                                    slot_meta.consumed,
-                                    slot_meta.completed_data_indexes,
-                                    start_index,
-                                    end_index
-                                );
-                            } else {
-                                return Err(BlockstoreError::InvalidShredData(Box::new(
-                                    bincode::ErrorKind::Custom(format!(
-                                        "Missing shred for slot {}, index {}",
-                                        slot, i
-                                    )),
-                                )));
+                                if slot > self.lowest_cleanup_slot() {
+                                    panic!(
+                                        "Shred with
+                                        slot: {},
+                                        index: {},
+                                        consumed: {},
+                                        completed_indexes: {:?}
+                                        must exist if shred index was included in a range: {} {}",
+                                        slot,
+                                        i,
+                                        slot_meta.consumed,
+                                        slot_meta.completed_data_indexes,
+                                        start_index,
+                                        end_index
+                                    );
+                                }
                             }
+                            return Err(BlockstoreError::InvalidShredData(Box::new(
+                                bincode::ErrorKind::Custom(format!(
+                                    "Missing shred for slot {}, index {}",
+                                    slot, i
+                                )),
+                            )));
                         }
 
                         Shred::new_from_serialized_shred(serialized_shred.unwrap()).map_err(|err| {
```
