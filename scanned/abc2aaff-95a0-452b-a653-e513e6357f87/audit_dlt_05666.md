# [?] Fix Rayon deadlock in test utils (#4837)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2023-10-18
Source: https://github.com/sigp/lighthouse/commit/192d44271849e744fc7ec0c574c6564eea49f015
Type: security-commit

## Details
Fix Rayon deadlock in test utils (#4837)

## Issue Addressed

Fix a deadlock in the tests that was causing tests on tree-states to run for hours without finishing: https://github.com/sigp/lighthouse/actions/runs/6491194654/job/17628138360.

## Proposed Changes

Avoid using a Mutex under the Rayon `par_iter`. Instead, use an `AtomicUsize`. I've run the new version several times in a loop and it hasn't deadlocked (it was deadlocking consistently on tree-states).

## Additional Info

The same bug exists in unstable and tree-states, but I'm not sure why it was triggering so consistently on the tree-states branch.

## Patch
### beacon_node/beacon_chain/src/test_utils.rs
```diff
@@ -52,6 +52,7 @@ use std::collections::{HashMap, HashSet};
 use std::fmt;
 use std::marker::PhantomData;
 use std::str::FromStr;
+use std::sync::atomic::{AtomicUsize, Ordering};
 use std::sync::Arc;
 use std::time::Duration;
 use store::{config::StoreConfig, HotColdDB, ItemStore, LevelDB, MemoryStore};
@@ -1156,9 +1157,9 @@ where
     ) -> (Vec<CommitteeAttestations<E>>, Vec<usize>) {
         let MakeAttestationOptions { limit, fork } = opts;
         let committee_count = state.get_committee_count_at_slot(state.slot()).unwrap();
-        let attesters = Mutex::new(vec![]);
+        let num_attesters = AtomicUsize::new(0);
 
-        let attestations = state
+        let (attestations, split_attesters) = state
             .get_beacon_committees_at_slot(attestation_slot)
             .expect("should get committees")
             .iter()
@@ -1171,13 +1172,14 @@ where
                             return None;
                         }
 
-                        let mut attesters = attesters.lock();
                         if let Some(limit) = limit {
-                            if attesters.len() >= limit {
+                            // This atomics stuff is necessary because we're under a par_iter,
+                            // and Rayon will deadlock if we use a mutex.
+                            if num_attesters.fetch_add(1, Ordering::Relaxed) >= limit {
+                                num_attesters.fetch_sub(1, Ordering::Relaxed);
                                 return None;
                             }
                         }
-                        attesters.push(*validator_index);
 
                         let mut attestation = self
                             .produce_unaggregated_attestation_for_block(
@@ -1217,14 +1219,17 @@ where
                         )
                         .unwrap();
 
-                        Some((attestation, subnet_id))
+                        Some(((attestation, subnet_id), validator_index))
                     })
-                    .collect::<Vec<_>>()
+                    .unzip::<_, _, Vec<_>, Vec<_>>()
             })
-            .collect::<Vec<_>>();
+            .unzip::<_, _, Vec<_>, Vec<_>>();
+
+        // Flatten attesters.
+        let attesters = split_attesters.into_iter().flatten().collect::<Vec<_>>();
 
-        let attesters = attesters.into_inner();
         if let Some(limit) = limit {
+            assert_eq!(limit, num_attesters.load(Ordering::Relaxed));
             assert_eq!(
                 limit,
                 attesters.len(),
```
