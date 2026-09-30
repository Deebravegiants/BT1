# [?] fix(storage/event): fix handling of page overflow for last block in range

## Summary
Severity: Unknown
Chain: Starknet
Component: eqlabs/pathfinder
Published: 2024-03-07
Source: https://github.com/software-mansion/pathfinder/commit/fded7afd969d2832eb2b63d2db6ba17a28d4801f
Type: security-commit

## Details
fix(storage/event): fix handling of page overflow for last block in range

Previously we did the is-page-full check _after_ increasing the current
block number and checking if we're out of the range in the filter.

This causes the code to behave like it's done scanning the block range
even if not all events from the last block fit into the page.

This change fixes the issue by moving the check right after the
potentially page-filling `scan_block_into()` call.

## Patch
### crates/storage/src/connection/event.rs
```diff
@@ -120,11 +120,6 @@ pub(super) fn get_events(
             break ScanResult::Done;
         }
 
-        // Stop if we have a page of events plus an extra one to decide if we're on the last page.
-        if emitted_events.len() > filter.page_size {
-            break ScanResult::PageFull;
-        }
-
         // Check bloom filter
         if !key_filter_is_empty || filter.contract_address.is_some() {
             let bloom = load_bloom(tx, reorg_counter, block_number)?;
@@ -169,6 +164,11 @@ pub(super) fn get_events(
             }
         }
 
+        // Stop if we have a page of events plus an extra one to decide if we're on the last page.
+        if emitted_events.len() > filter.page_size {
+            break ScanResult::PageFull;
+        }
+
         block_number += 1;
 
         // Check if we've reached our Bloom filter load limit
@@ -601,6 +601,69 @@ mod tests {
         );
     }
 
+    #[test]
+    fn get_events_up_to_block_with_paging() {
+        let (storage, test_data) = test_utils::setup_test_storage();
+        let emitted_events = test_data.events;
+        let mut connection = storage.connection().unwrap();
+        let tx = connection.transaction().unwrap();
+
+        let filter = EventFilter {
+            from_block: None,
+            to_block: Some(BlockNumber::new_or_panic(1)),
+            contract_address: None,
+            keys: vec![],
+            page_size: test_utils::EVENTS_PER_BLOCK + 1,
+            offset: 0,
+        };
+
+        let expected_events = &emitted_events[..test_utils::EVENTS_PER_BLOCK + 1];
+        let events = get_events(
+            &tx,
+            &filter,
+            *MAX_BLOCKS_TO_SCAN,
+            *MAX_BLOOM_FILTERS_TO_LOAD,
+        )
+        .unwrap();
+        pretty_assertions_sorted::assert_eq!(
+            events,
+            PageOfEvents {
+                events: expected_events.to_vec(),
+                continuation_token: Some(ContinuationToken {
+                    block_number: BlockNumber::new_or_panic(1),
+                    offset: 1
+                }),
+            }
+        );
+
+        // test continuation token
+        let filter = EventFilter {
+            from_block: Some(events.continuation_token.unwrap().block_number),
+            to_block: Some(BlockNumber::new_or_panic(1)),
+            contract_address: None,
+            keys: vec![],
+            page_size: test_utils::EVENTS_PER_BLOCK + 1,
+            offset: events.continuation_token.unwrap().offset,
+        };
+
+        let expected_events =
+            &emitted_events[test_utils::EVENTS_PER_BLOCK + 1..test_utils::EVENTS_PER_BLOCK * 2];
+        let events = get_events(
+            &tx,
+            &filter,
+            *MAX_BLOCKS_TO_SCAN,
+            *MAX_BLOOM_FILTERS_TO_LOAD,
+        )
+        .unwrap();
+        pretty_assertions_sorted::assert_eq!(
+            events,
+            PageOfEvents {
+                events: expected_events.to_vec(),
+                continuation_token: None,
+            }
+        );
+    }
+
     #[test]
     fn get_events_from_block_onwards() {
         let (storage, test_data) = test_utils::setup_test_storage();
```
