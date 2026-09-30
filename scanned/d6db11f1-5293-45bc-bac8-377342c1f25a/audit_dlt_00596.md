# [?] Fix O(n²) find_head and stack overflow in filter_block_tree (#9090)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2026-06-05
Source: https://github.com/sigp/lighthouse/commit/494b00a3491e2c5e281f6972aa00694b17f16722
Type: security-commit

## Details
Fix O(n²) find_head and stack overflow in filter_block_tree (#9090)

Co-Authored-By: dapplion <35266934+dapplion@users.noreply.github.com>

Co-Authored-By: Michael Sproul <michaelsproul@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -7020,6 +7020,7 @@ dependencies = [
 name = "proto_array"
 version = "0.2.0"
 dependencies = [
+ "criterion",
  "ethereum_ssz",
  "ethereum_ssz_derive",
  "fixed_bytes",
```

### consensus/proto_array/Cargo.toml
```diff
@@ -19,3 +19,11 @@ superstruct = { workspace = true }
 typenum = { workspace = true }
 types = { workspace = true }
 yaml_serde = { workspace = true }
+
+[dev-dependencies]
+criterion = { workspace = true }
+fixed_bytes = { workspace = true }
+
+[[bench]]
+name = "find_head"
+harness = false
```

### consensus/proto_array/benches/find_head.rs
```diff
@@ -0,0 +1,118 @@
+use criterion::{BenchmarkId, Criterion, criterion_group, criterion_main};
+use fixed_bytes::FixedBytesExtended;
+use proto_array::{Block, ExecutionStatus, JustifiedBalances, ProtoArrayForkChoice};
+use std::collections::BTreeSet;
+use std::time::Duration;
+use types::{
+    AttestationShufflingId, Checkpoint, Epoch, EthSpec, ExecutionBlockHash, Hash256,
+    MainnetEthSpec, Slot,
+};
+
+fn get_root(i: u64) -> Hash256 {
+    Hash256::from_low_u64_be(i)
+}
+
+fn get_hash(i: u64) -> ExecutionBlockHash {
+    ExecutionBlockHash::from_root(get_root(i))
+}
+
+/// Build a linear chain of `num_blocks` blocks.
+fn build_chain(num_blocks: u64, gloas: bool) -> (ProtoArrayForkChoice, types::ChainSpec) {
+    let mut spec = MainnetEthSpec::default_spec();
+    let gloas_fork_slot = 32;
+    if gloas {
+        spec.gloas_fork_epoch = Some(Epoch::new(1));
+    }
+
+    let finalized_checkpoint = Checkpoint {
+        epoch: Epoch::new(0),
+        root: get_root(0),
+    };
+    let junk_shuffling_id = AttestationShufflingId::from_components(Epoch::new(0), Hash256::zero());
+
+    let mut fork_choice = ProtoArrayForkChoice::new::<MainnetEthSpec>(
+        Slot::new(0),
+        Slot::new(0),
+        Hash256::zero(),
+        finalized_checkpoint,
+        finalized_checkpoint,
+        junk_shuffling_id.clone(),
+        junk_shuffling_id.clone(),
+        ExecutionStatus::Optimistic(ExecutionBlockHash::zero()),
+        None,
+        None,
+        0,
+        &spec,
+    )
+    .expect("should create fork choice");
+
+    for i in 1..=num_blocks {
+        let is_gloas = gloas && i >= gloas_fork_slot;
+        let block = Block {
+            slot: Slot::new(i),
+            root: get_root(i),
+            parent_root: Some(get_root(i - 1)),
+            state_root: Hash256::zero(),
+            target_root: get_root(0),
+            current_epoch_shuffling_id: junk_shuffling_id.clone(),
+            next_epoch_shuffling_id: junk_shuffling_id.clone(),
+            justified_checkpoint: finalized_checkpoint,
+            finalized_checkpoint,
+            execution_status: ExecutionStatus::Optimistic(ExecutionBlockHash::zero()),
+            unrealized_justified_checkpoint: Some(finalized_checkpoint),
+            unrealized_finalized_checkpoint: Some(finalized_checkpoint),
+            execution_payload_parent_hash: if is_gloas {
+                Some(get_hash(i - 1))
+            } else {
+                None
+            },
+            execution_payload_block_hash: if is_gloas { Some(get_hash(i)) } else { None },
+            proposer_index: Some(0),
+        };
+
+        fork_choice
+            .process_block::<MainnetEthSpec>(block, Slot::new(i), &spec, Duration::ZERO)
+            .expect("should process block");
+    }
+
+    (fork_choice, spec)
+}
+
+fn bench_find_head(c: &mut Criterion) {
+    let mut group = c.benchmark_group("find_head");
+    let equivocating_indices = BTreeSet::new();
+    let finalized_checkpoint = Checkpoint {
+        epoch: Epoch::new(0),
+        root: get_root(0),
+    };
+    let balances = JustifiedBalances::from_effective_balances(vec![1; 64]).unwrap();
+
+    // 216k = ~1 month non-finality mainnet, 518k = ~1 month non-finality Gnosis.
+    // Must survive extended non-finality (500k+ blocks).
+    for (label, gloas) in [("pre_gloas", false), ("gloas", true)] {
+        for &num_blocks in &[100, 1_000, 10_000, 50_000, 216_000, 518_000] {
+            let (mut fork_choice, spec) = build_chain(num_blocks, gloas);
+
+            group.bench_function(BenchmarkId::new(label, num_blocks), |b| {
+                b.iter(|| {
+                    fork_choice
+                        .find_head::<MainnetEthSpec>(
+                            finalized_checkpoint,
+                            finalized_checkpoint,
+                            &balances,
+                            Hash256::zero(),
+                            &equivocating_indices,
+                            Slot::new(num_blocks),
+                            &spec,
+                        )
+                        .expect("should find head")
+                });
+            });
+        }
+    }
+
+    group.finish();
+}
+
+criterion_group!(benches, bench_find_head);
+criterion_main!(benches);
```

### consensus/proto_array/src/proto_array.rs
```diff
@@ -391,6 +391,10 @@ pub struct ProtoArray {
     pub prune_threshold: usize,
     pub nodes: Vec<ProtoNode>,
     pub indices: HashMap<Hash256, usize>,
+    /// Cached parent→children index. `children[i]` holds the node indices of all children of
+    /// node `i`. Maintained incrementally by `on_block` and `maybe_prune`.
+    #[serde(skip)]
+    pub children: Vec<Vec<usize>>,
 }
 
 impl ProtoArray {
@@ -673,6 +677,16 @@ impl ProtoArray {
         self.indices.insert(node.root(), node_index);
         self.nodes.push(node.clone());
 
+        // Maintain cached children index. `parent_index` is already bounds-checked above
+        // against `self.nodes`, and `self.children` is kept in lockstep with `self.nodes`.
+        self.children.push(Vec::new());
+        if let Some(parent_index) = node.parent() {
+            self.children
+                .get_mut(parent_index)
+                .ok_or(Error::InvalidNodeIndex(parent_index))?
+                .push(node_index);
+        }
+
         if let Some(parent_index) = node.parent()
             && matches!(block.execution_status, ExecutionStatus::Valid(_))
         {
@@ -1095,6 +1109,22 @@ impl ProtoArray {
         Ok((best_fc_node.root, best_fc_node.payload_status))
     }
 
+    /// Rebuild the cached `self.children` index from `self.nodes`. Called once after
+    /// deserialization to populate the transient field.
+    pub fn rebuild_children_index(&mut self) -> Result<(), Error> {
+        let mut children = vec![Vec::new(); self.nodes.len()];
+        for (i, node) in self.nodes.iter().enumerate() {
+            if let Some(parent_idx) = node.parent() {
+                children
+                    .get_mut(parent_idx)
+                    .ok_or(Error::InvalidNodeIndex(parent_idx))?
+                    .push(i);
+            }
+        }
+        self.children = children;
+        Ok(())
+    }
+
     /// Spec: `get_filtered_block_tree`.
     ///
     /// Returns the set of node indices on viable branches — those with at least
@@ -1105,79 +1135,96 @@ impl ProtoArray {
         current_slot: Slot,
         best_justified_checkpoint: Checkpoint,
         best_finalized_checkpoint: Checkpoint,
-    ) -> HashSet<usize> {
+    ) -> Result<HashSet<usize>, Error> {
         let mut viable = HashSet::new();
         self.filter_block_tree::<E>(
             start_index,
             current_slot,
             best_justified_checkpoint,
             best_finalized_checkpoint,
             &mut viable,
-        );
-        viable
+        )?;
+        Ok(viable)
     }
 
     /// Spec: `filter_block_tree`.
+    ///
+    /// Proto_array stores nodes in insertion order — children always have higher
+    /// indices than their parents. A single reverse pass therefore processes every
+    /// child before its parent, matching the spec's recursive post-order semantics
+    /// without recursion (required to survive 500k+ blocks of non-finality).
+    ///
+    /// The spec removes execution-invalid blocks (and their entire subtrees) from
+    /// `store.blocks` before running. We replicate that here with a forward pass
+    /// propagating `excluded` from parent to child — V29 children of an invalidated
+    /// V17 ancestor are excluded transitively, since V29 nodes carry no
+    /// `execution_status` of their own.
     fn filter_block_tree<E: EthSpec>(
         &self,
-        node_index: usize,
+        start_index: usize,
         current_slot: Slot,
         best_justified_checkpoint: Checkpoint,
         best_finalized_checkpoint: Checkpoint,
         viable: &mut HashSet<usize>,
-    ) -> bool {
-        let Some(node) = self.nodes.get(node_index) else {
-            return false;
-        };
+    ) -> Result<(), Error> {
+        // Forward pass: a node is "excluded" if it (or any ancestor down to
+        // `start_index`) has an invalid execution status.
+        let mut excluded = vec![false; self.nodes.len()];
+        for i in (start_index + 1)..self.nodes.len() {
+            let node = self.nodes.get(i).ok_or(Error::InvalidNodeIndex(i))?;
+            let parent_excluded = match node.parent() {
+                Some(p) => *excluded.get(p).ok_or(Error::InvalidNodeIndex(p))?,
+                None => false,
+            };
+            let self_invalid = node.execution_status().is_ok_and(|s| s.is_invalid());
+            excluded[i] = parent_excluded || self_invalid;
+        }
 
-        // Skip invalid children — they aren't in store.blocks in the spec.
-        let children: Vec<usize> = self
-            .nodes
-            .iter()
-            .enumerate()
-            .filter(|(_, child)| {
-                child.parent() == Some(node_index)
-                    && !child
-                        .execution_status()
-                        .is_ok_and(|status| status.is_invalid())
-            })
-            .map(|(i, _)| i)
-            .collect();
+        for node_index in (start_index..self.nodes.len()).rev() {
+            // Spec: invalid subtree removed from `store.blocks` — skip entirely.
+            if *excluded
+                .get(node_index)
+                .ok_or(Error::InvalidNodeIndex(node_index))?
+            {
+                continue;
+            }
+            let node = self
+                .nodes
+                .get(node_index)
+                .ok_or(Error::InvalidNodeIndex(node_index))?;
 
-        if !children.is_empty() {
-            // Evaluate ALL children (no short-circuit) to mark all viable branches.
-            let any_viable = children
+            // Spec: children = [root for root in blocks if blocks[root].parent_root == block_root]
+            let valid_children: Vec<usize> = self
+                .children
+                .get(node_index)
+                .ok_or(Error::InvalidNodeIndex(node_index))?
                 .iter()
-                .map(|&child_index| {
-                    self.filter_block_tree::<E>(
-                        child_index,
-                        current_slot,
-                        best_justified_checkpoint,
-                        best_finalized_checkpoint,
-                        viable,
-                    )
+                .copied()
+                .filter_map(|i| match excluded.get(i) {
+                    Some(false) => Some(Ok(i)),
+                    Some(true) => None,
+                    None => Some(Err(Error::InvalidNodeIndex(i))),
                 })
-                .collect::<Vec<_>>()
-                .into_iter()
-                .any(|v| v);
-            if any_viable {
-                viable.insert(node_index);
-                return true;
-            }
-            return false;
-        }
+                .collect::<Result<_, _>>()?;
 
-        // Leaf node: check viability.
-        if self.node_is_viable_for_head::<E>(
-            node,
-            current_slot,
-            best_justified_checkpoint,
-            best_finalized_checkpoint,
-        ) {
-            viable.insert(node_index);
-            return true;
+            if !valid_children.is_empty() {
+                // Spec: if any(children): if any(filter_block_tree_result): blocks[block_root] = block
+                if valid_children.iter().any(|c| viable.contains(c)) {
+                    viable.insert(node_index);
+                }
+            } else {
+                // Spec: leaf — check correct_justified and correct_finalized
+                if self.node_is_viable_for_head::<E>(
+                    node,
+                    current_slot,
+                    best_justified_checkpoint,
+                    best_finalized_checkpoint,
+                ) {
+                    viable.insert(node_index);
+                }
+            }
         }
-        false
+        Ok(())
     }
 
     /// Spec: `get_head`.
@@ -1204,7 +1251,7 @@ impl ProtoArray {
             current_slot,
             best_justified_checkpoint,
             best_finalized_checkpoint,
-        );
+        )?;
 
         // Compute once rather than per-child per-level.
         let apply_proposer_boost =
@@ -1468,25 +1515,35 @@ impl ProtoArray {
             }
             Ok(children)
         } else {
-            Ok(self
-                .nodes
+            // Spec: [root for root in blocks.keys() if blocks[root].parent_root == node.root ...]
+            // (cached `self.children[i]` is the same set as the spec's filtered scan).
+            let indices = self
+                .children
+                .get(node.proto_node_index)
+                .ok_or(Error::InvalidNodeIndex(node.proto_node_index))?;
+            indices
                 .iter()
-                .enumerate()
-                .filter(|(_, child_node)| {
-                    child_node.parent() == Some(node.proto_node_index)
-                        && child_node.get_parent_payload_status() == node.payload_status
-                })
-                .map(|(child_index, child_node)| {
-                    (
-                        IndexedForkChoiceNode {
-                            root: child_node.root(),
-                            proto_node_index: child_index,
-                            payload_status: PayloadStatus::Pending,
-                        },
-                        child_node.clone(),
-                    )
+                .copied()
+                .filter_map(|i| {
+                    self.nodes
+                        .get(i)
+                        .ok_or(Error::InvalidNodeIndex(i))
+                        .map(|child| {
+                            // Spec: node.payload_status == get_parent_payload_status(store, blocks[root])
+                            (child.get_parent_payload_status() == node.payload_status).then(|| {
+                                (
+                                    IndexedForkChoiceNode {
+                                        root: child.root(),
+                                        proto_node_index: i,
+                                        payload_status: PayloadStatus::Pending,
+                                    },
+                                    child.clone(),
+                                )
+                            })
+                        })
+                        .transpose()
                 })
-                .collect())
+                .collect()
         }
     }
 
@@ -1617,6 +1674,19 @@ impl ProtoArray {
         // Drop all the nodes prior to finalization.
         self.nodes = self.nodes.split_off(finalized_index);
 
+        // Drop pruned entries from children index and shift all remaining indices down.
+        // Invariant: child_index > parent_index, and all parents we kept have
+        // index >= finalized_index, so every remaining child_index is also
+        // >= finalized_index.
+        self.children = self.children.split_off(finalized_index);
+        for children in self.children.iter_mut() {
+            for child_index in children.iter_mut() {
+                *child_index = child_index
+                    .checked_sub(finalized_index)
+                    .ok_or(Error::IndexOverflow("children"))?;
+            }
+        }
+
         // Adjust the indices map.
         for (_root, index) in self.indices.iter_mut() {
             *index = index
```

### consensus/proto_array/src/proto_array_fork_choice.rs
```diff
@@ -514,6 +514,7 @@ impl ProtoArrayForkChoice {
             prune_threshold: DEFAULT_PRUNE_THRESHOLD,
             nodes: Vec::with_capacity(1),
             indices: HashMap::with_capacity(1),
+            children: Vec::with_capacity(1),
         };
 
         let block = Block {
```

### consensus/proto_array/src/ssz_container.rs
```diff
@@ -59,11 +59,13 @@ impl TryFrom<(SszContainerV29, JustifiedBalances)> for ProtoArrayForkChoice {
     type Error = Error;
 
     fn try_from((from, balances): (SszContainerV29, JustifiedBalances)) -> Result<Self, Error> {
-        let proto_array = ProtoArray {
+        let mut proto_array = ProtoArray {
             prune_threshold: from.prune_threshold,
             nodes: from.nodes,
             indices: from.indices.into_iter().collect::<HashMap<_, _>>(),
+            children: Vec::new(),
         };
+        proto_array.rebuild_children_index()?;
 
         Ok(Self {
             proto_array,
```
