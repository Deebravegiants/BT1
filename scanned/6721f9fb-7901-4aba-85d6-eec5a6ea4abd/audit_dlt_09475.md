# [?] Added a regression test documenting the faulty state of the node which can occur if a validating node comes back up after a crash and tries to validat

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2026-04-20
Source: https://github.com/casper-network/casper-node/commit/44508b26fd1e8e998b393126e7b9eb520c3f81bb
Type: security-commit

## Details
Added a regression test documenting the faulty state of the node which can occur if a validating node comes back up after a crash and tries to validate finality signatures from a previous era

## Patch
### Cargo.lock
```diff
@@ -8070,4 +8070,4 @@ dependencies = [
  "proc-macro2",
  "quote",
  "syn 2.0.101",
-]
+]
\ No newline at end of file
```

### node/src/reactor/main_reactor/tests.rs
```diff
@@ -6,6 +6,7 @@ mod fixture;
 mod gas_price;
 mod initial_stakes;
 mod network_general;
+mod rejoining_node;
 mod rewards;
 mod switch_blocks;
 mod transaction_scenario;
```

### node/src/reactor/main_reactor/tests/fixture.rs
```diff
@@ -31,15 +31,20 @@ use casper_types::{
 use crate::{
     components::{gossiper, network, storage},
     effect::EffectExt,
-    reactor::main_reactor::{
-        tests::{
-            configs_override::{ConfigsOverride, NodeConfigOverride},
-            initial_stakes::InitialStakes,
-            Nodes, ERA_TWO,
+    reactor::{
+        main_reactor::{
+            tests::{
+                configs_override::{ConfigsOverride, NodeConfigOverride},
+                initial_stakes::InitialStakes,
+                Nodes, ERA_TWO,
+            },
+            Config, MainReactor, ReactorState,
         },
-        Config, MainReactor, ReactorState,
+        Runner,
+    },
+    testing::{
+        self, filter_reactor::FilterReactor, network::TestingNetwork, ConditionCheckReactor,
     },
-    testing::{self, filter_reactor::FilterReactor, network::TestingNetwork},
     types::NodeId,
     utils::{External, Loadable, Source, RESOURCES_PATH},
     WithDir,
@@ -49,7 +54,7 @@ pub(crate) struct NodeContext {
     pub id: NodeId,
     pub secret_key: Arc<SecretKey>,
     pub config: Config,
-    pub storage_dir: TempDir,
+    pub storage_dir: Arc<TempDir>,
 }
 
 pub(crate) struct TestFixture {
@@ -373,7 +378,7 @@ impl TestFixture {
         maybe_trusted_hash: Option<BlockHash>,
         storage_multiplier: u8,
         node_config_override: NodeConfigOverride,
-    ) -> (Config, TempDir) {
+    ) -> (Config, Arc<TempDir>) {
         // Set the network configuration.
         let network_cfg = match self.node_contexts.first() {
             Some(first_node) => {
@@ -419,7 +424,7 @@ impl TestFixture {
         cfg.contract_runtime.max_global_state_size =
             Some(1024 * 1024 * storage_multiplier as usize);
 
-        (cfg, temp_dir)
+        (cfg, Arc::new(temp_dir))
     }
 
     /// Adds a node to the network.
@@ -431,7 +436,7 @@ impl TestFixture {
         &mut self,
         secret_key: Arc<SecretKey>,
         config: Config,
-        storage_dir: TempDir,
+        storage_dir: Arc<TempDir>,
     ) -> NodeId {
         let (id, _) = self
             .network
@@ -454,6 +459,14 @@ impl TestFixture {
         id
     }
 
+    pub(crate) async fn add_node_from_context_idx(&mut self, idx: usize) -> NodeId {
+        let node_context = self.node_contexts.get(idx).unwrap();
+        let secret_key = node_context.secret_key.clone();
+        let config = node_context.config.clone();
+        let storage_dir = node_context.storage_dir.clone();
+        self.add_node(secret_key, config, storage_dir).await
+    }
+
     #[track_caller]
     pub(crate) fn remove_and_stop_node(&mut self, index: usize) -> NodeContext {
         let node_context = self.node_contexts.remove(index);
@@ -915,6 +928,18 @@ impl TestFixture {
         &mut self.network
     }
 
+    /// Removes a node from the network.
+    pub(crate) fn remove_node_by_idx(
+        &mut self,
+        idx: usize,
+    ) -> Runner<ConditionCheckReactor<FilterReactor<MainReactor>>> {
+        let node_id = {
+            let context = self.node_contexts.get(idx).unwrap();
+            context.id
+        };
+        self.network_mut().remove_node(&node_id).unwrap()
+    }
+
     pub(crate) fn run_until_stopped(
         self,
         rng: TestRng,
```

### node/src/reactor/main_reactor/tests/rejoining_node.rs
```diff
@@ -0,0 +1,79 @@
+use crate::reactor::main_reactor::{
+    tests::{
+        configs_override::ConfigsOverride, fixture::TestFixture, initial_stakes::InitialStakes,
+        Nodes, ERA_TWO, ONE_MIN,
+    },
+    ReactorState,
+};
+
+/*
+  Scenario:
+  In Era_1 the node crashes towards the end of the era.
+  The node comes back up in Era_2 and needs to validate a finality signature from Era_1
+  The node should have enough validator awareness for the BlockValidator not to crash the
+  node (it was a bug before)
+*/
+#[tokio::test]
+async fn should_recover_after_rejoin_when_node_has_unfinished_business_in_previous_era() {
+    let alice_stake = 100_000_000_000_u64;
+    let bob_stake = 100_000_000_000_u64;
+    let charlie_stake = 100_000_000_000_u64;
+    let fourth_stake = 120_000_000_000_u64;
+    let initial_stakes = InitialStakes::FromVec(vec![
+        alice_stake.into(),
+        bob_stake.into(),
+        charlie_stake.into(),
+        fourth_stake.into(),
+    ]);
+
+    let mut fixture = TestFixture::new(
+        initial_stakes,
+        Some(ConfigsOverride {
+            minimum_block_time: "5second".parse().unwrap(),
+            minimum_era_height: 5,
+            ..Default::default()
+        }),
+    )
+    .await;
+    fixture.run_until_block_height(3, ONE_MIN).await;
+
+    // Node 4 goes down - when it comes back up it will
+    // still want to sign over at least 2 of the blocks from Era 1
+    fixture.remove_node_by_idx(3);
+    fixture.run_until_block_height(6, ONE_MIN).await;
+
+    // We should be now in Era 2. Node 4 is still down.
+    // When node 4 will go back up - we don't know which of the nodes will be proposing
+    // the new block which cites node_4 signatures over block_4 and block_5. That is a
+    // problem because the test would be non-deterministic (node 1-3 have their
+    // validator matrix filled with Era 1 and Era 2 data). To push the network into the edge
+    // case we force a restart on all of the nodes to see if the validator matrixes will
+    // get reinitialized correctly.
+    fixture.remove_node_by_idx(0);
+    fixture.remove_node_by_idx(1);
+    fixture.remove_node_by_idx(2);
+    fixture.add_node_from_context_idx(0).await;
+    fixture.add_node_from_context_idx(1).await;
+    fixture.add_node_from_context_idx(2).await;
+    fixture.add_node_from_context_idx(3).await;
+
+    // Wait for the network to start validating
+    fixture
+        .run_until(
+            move |nodes: &Nodes| {
+                nodes.values().all(|runner| {
+                    let state = runner.main_reactor().state;
+                    matches!(state, ReactorState::Validate)
+                })
+            },
+            ONE_MIN,
+        )
+        .await;
+
+    // Node 4 should eventually send out it's signatures over B_4 and B_5.
+    // Whichever node will produce the block citing those signatures should be after a fresh restart
+    // and if we progress to Era 3 without error it means that we are in the clear.
+    fixture
+        .run_until_stored_switch_block_header(ERA_TWO, ONE_MIN)
+        .await;
+}
```
