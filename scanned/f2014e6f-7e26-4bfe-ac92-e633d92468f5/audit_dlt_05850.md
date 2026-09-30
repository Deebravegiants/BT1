# [?] fix: allow panic_with_no_subnet_record in //rs/tests/nns:delete_subnet_test (#10039)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-04-28
Source: https://github.com/dfinity/ic/commit/fd0179fced559f5c9c8d074ff3440386404e7b8c
Type: security-commit

## Details
fix: allow panic_with_no_subnet_record in //rs/tests/nns:delete_subnet_test (#10039)

The `//rs/tests/nns:delete_subnet_test` would sometimes flake with:
```
Task assert_no_unallowed_log_patterns FAILED  in   0.13s
     Found unallowed log patterns in IC logs for group `delete-subnet-test--1777304524162056`:
     - Pattern `panicked`: 4 match(es)
         [2026-04-27T15:44:03.888270Z qis6x-cqfp3-tdpzb-xff7d-veukd-t6q63-dzqjb-2dbdf-jnoxu-gmqsg-tae] thread 'consensus_Processor' (1450) panicked at rs/consensus/src/consensus.rs:357:17:
         [2026-04-27T15:44:05.112477Z kouz2-swfzy-zjmx6-emb7x-keyk5-pwqzk-iqvsa-cdlhp-3kred-zk74b-gqe] thread 'consensus_Processor' (1448) panicked at rs/consensus/src/consensus.rs:357:17:
         [2026-04-27T15:44:03.888810Z vs5cs-seu3u-e365w-ksb63-lin7b-2m7ll-4jx54-hlpsz-bab5j-ksn2c-bqe] thread 'consensus_Processor' (1387) panicked at rs/consensus/src/consensus.rs:357:17:
         ... and 1 more
```
This is because subnet deletion deletes the subnet record. The replica
currently panics if it notices the missing subnet record before it is
killed by the orchestrator. The reason it's flaky is because the panic
races against the orchestrator killing the replica. If the panic is
first we hit the flake, if the orchestrator kills the replica first the
test passes.

We fix this by allowing the specific `panic_with_no_subnet_record` in
the `delete_subnet_test`.

## Patch
### rs/consensus/src/consensus.rs
```diff
@@ -1,6 +1,7 @@
 //! This module encapsulates all components required for establishing of a
 //! distributed consensus.
 
+mod allowed_panics;
 pub mod batch_delivery;
 mod block_maker;
 pub mod bounds;
@@ -24,10 +25,11 @@ pub mod validator;
 mod proptests;
 
 use crate::consensus::{
-    block_maker::BlockMaker, catchup_package_maker::CatchUpPackageMaker, finalizer::Finalizer,
-    metrics::ConsensusMetrics, notary::Notary, payload_builder::PayloadBuilderImpl,
-    priority::new_bouncer, purger::Purger, random_beacon_maker::RandomBeaconMaker,
-    random_tape_maker::RandomTapeMaker, share_aggregator::ShareAggregator, validator::Validator,
+    allowed_panics::panic_with_no_subnet_record, block_maker::BlockMaker,
+    catchup_package_maker::CatchUpPackageMaker, finalizer::Finalizer, metrics::ConsensusMetrics,
+    notary::Notary, payload_builder::PayloadBuilderImpl, priority::new_bouncer, purger::Purger,
+    random_beacon_maker::RandomBeaconMaker, random_tape_maker::RandomTapeMaker,
+    share_aggregator::ShareAggregator, validator::Validator,
 };
 use ic_consensus_dkg::DkgKeyManager;
 use ic_consensus_utils::{
@@ -354,10 +356,7 @@ impl ConsensusImpl {
             .get_is_halted(self.replica_config.subnet_id, version)
         {
             Ok(None) => {
-                panic!(
-                    "No subnet record found for registry version={:?} and subnet_id={:?}",
-                    version, self.replica_config.subnet_id,
-                );
+                panic_with_no_subnet_record(version, self.replica_config.subnet_id);
             }
             Err(err) => {
                 error!(
```

### rs/consensus/src/consensus/allowed_panics.rs
```diff
@@ -0,0 +1,9 @@
+//! This module contains panics that are allowed by default to occur in logs in system-tests.
+use ic_types::{RegistryVersion, SubnetId};
+
+pub(crate) fn panic_with_no_subnet_record(version: RegistryVersion, subnet_id: SubnetId) -> ! {
+    panic!(
+        "No subnet record found for registry version={:?} and subnet_id={:?}",
+        version, subnet_id,
+    )
+}
```

### rs/tests/nns/delete_subnet_test.rs
```diff
@@ -35,6 +35,10 @@ fn main() -> Result<()> {
     SystemTestGroup::new()
         .with_setup(setup)
         .add_test(systest!(test))
+        .add_unallowed_log_pattern_except(
+            "panicked",
+            "rs/consensus/src/consensus/allowed_panics.rs",
+        )
         .execute_from_args()?;
     Ok(())
 }
```
