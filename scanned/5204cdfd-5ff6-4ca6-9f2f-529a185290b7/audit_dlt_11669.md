# [?] fix(chain): Correctly handle txs that double spend themselves

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2025-03-28
Source: https://github.com/bitcoindevkit/bdk/commit/370497c3a9c361e10c8341cbb07210f026cc3e04
Type: security-commit

## Details
fix(chain): Correctly handle txs that double spend themselves

Detect self-double-spends in `CanonicalIter::mark_canonical`. Disregard
the tx that self-double-spends and all it's attached meta data (such as
timestamps and anchors).

Add new test cases on `test_tx_conflict_handling` for transactions that
self-double-spend.

## Patch
### crates/chain/src/canonical_iter.rs
```diff
@@ -1,12 +1,16 @@
-use crate::collections::{hash_map, HashMap, HashSet, VecDeque};
+use crate::collections::{HashMap, HashSet, VecDeque};
 use crate::tx_graph::{TxAncestors, TxDescendants};
 use crate::{Anchor, ChainOracle, TxGraph};
 use alloc::boxed::Box;
 use alloc::collections::BTreeSet;
 use alloc::sync::Arc;
+use alloc::vec::Vec;
 use bdk_core::BlockId;
 use bitcoin::{Transaction, Txid};
 
+type CanonicalMap<A> = HashMap<Txid, (Arc<Transaction>, CanonicalReason<A>)>;
+type NotCanonicalSet = HashSet<Txid>;
+
 /// Iterates over canonical txs.
 pub struct CanonicalIter<'g, A, C> {
     tx_graph: &'g TxGraph<A>,
@@ -18,8 +22,8 @@ pub struct CanonicalIter<'g, A, C> {
     unprocessed_txs_with_last_seens: Box<dyn Iterator<Item = (Txid, Arc<Transaction>, u64)> + 'g>,
     unprocessed_txs_left_over: VecDeque<(Txid, Arc<Transaction>, u32)>,
 
-    canonical: HashMap<Txid, (Arc<Transaction>, CanonicalReason<A>)>,
-    not_canonical: HashSet<Txid>,
+    canonical: CanonicalMap<A>,
+    not_canonical: NotCanonicalSet,
 
     queue: VecDeque<Txid>,
 }
@@ -87,27 +91,49 @@ impl<'g, A: Anchor, C: ChainOracle> CanonicalIter<'g, A, C> {
         Ok(())
     }
 
-    /// Marks a transaction and it's ancestors as canonical. Mark all conflicts of these as
+    /// Marks `tx` and it's ancestors as canonical and mark all conflicts of these as
     /// `not_canonical`.
+    ///
+    /// The exception is when it is discovered that `tx` double spends itself (i.e. two of it's
+    /// inputs conflict with each other), then no changes will be made.
+    ///
+    /// The logic works by having two loops where one is nested in another.
+    /// * The outer loop iterates through ancestors of `tx` (including `tx`). We can transitively
+    ///   assume that all ancestors of `tx` are also canonical.
+    /// * The inner loop loops through conflicts of ancestors of `tx`. Any descendants of conflicts
+    ///   are also conflicts and are transitively considered non-canonical.
+    ///
+    /// If the inner loop ends up marking `tx` as non-canonical, then we know that it double spends
+    /// itself.
     fn mark_canonical(&mut self, txid: Txid, tx: Arc<Transaction>, reason: CanonicalReason<A>) {
         let starting_txid = txid;
-        let mut is_root = true;
-        TxAncestors::new_include_root(
+        let mut is_starting_tx = true;
+
+        // We keep track of changes made so far so that we can undo it later in case we detect that
+        // `tx` double spends itself.
+        let mut detected_self_double_spend = false;
+        let mut undo_not_canonical = Vec::<Txid>::new();
+
+        // `staged_queue` doubles as the `undo_canonical` data.
+        let staged_queue = TxAncestors::new_include_root(
             self.tx_graph,
             tx,
-            |_: usize, tx: Arc<Transaction>| -> Option<()> {
+            |_: usize, tx: Arc<Transaction>| -> Option<Txid> {
                 let this_txid = tx.compute_txid();
-                let this_reason = if is_root {
-                    is_root = false;
+                let this_reason = if is_starting_tx {
+                    is_starting_tx = false;
                     reason.clone()
                 } else {
                     reason.to_transitive(starting_txid)
                 };
+
+                use crate::collections::hash_map::Entry;
                 let canonical_entry = match self.canonical.entry(this_txid) {
                     // Already visited tx before, exit early.
-                    hash_map::Entry::Occupied(_) => return None,
-                    hash_map::Entry::Vacant(entry) => entry,
+                    Entry::Occupied(_) => return None,
+                    Entry::Vacant(entry) => entry,
                 };
+
                 // Any conflicts with a canonical tx can be added to `not_canonical`. Descendants
                 // of `not_canonical` txs can also be added to `not_canonical`.
                 for (_, conflict_txid) in self.tx_graph.direct_conflicts(&tx) {
@@ -116,6 +142,7 @@ impl<'g, A: Anchor, C: ChainOracle> CanonicalIter<'g, A, C> {
                         conflict_txid,
                         |_: usize, txid: Txid| -> Option<()> {
                             if self.not_canonical.insert(txid) {
+                                undo_not_canonical.push(txid);
                                 Some(())
                             } else {
                                 None
@@ -124,12 +151,28 @@ impl<'g, A: Anchor, C: ChainOracle> CanonicalIter<'g, A, C> {
                     )
                     .run_until_finished()
                 }
+
+                if self.not_canonical.contains(&this_txid) {
+                    // Early exit if self-double-spend is detected.
+                    detected_self_double_spend = true;
+                    return None;
+                }
                 canonical_entry.insert((tx, this_reason));
-                self.queue.push_back(this_txid);
-                Some(())
+                Some(this_txid)
             },
         )
-        .run_until_finished()
+        .collect::<Vec<Txid>>();
+
+        if detected_self_double_spend {
+            for txid in staged_queue {
+                self.canonical.remove(&txid);
+            }
+            for txid in undo_not_canonical {
+                self.not_canonical.remove(&txid);
+            }
+        } else {
+            self.queue.extend(staged_queue);
+        }
     }
 }
 
```

### crates/chain/tests/test_tx_graph_conflicts.rs
```diff
@@ -686,7 +686,111 @@ fn test_tx_conflict_handling() {
             exp_chain_txouts: HashSet::from([("tx", 0)]),
             exp_unspents: HashSet::from([("tx", 0)]),
             exp_balance: Balance { trusted_pending: Amount::from_sat(9000), ..Default::default() }
-        }
+        },
+        Scenario {
+            name: "tx spends from 2 conflicting transactions where a conflict spends another",
+            tx_templates: &[
+                TxTemplate {
+                    tx_name: "A",
+                    inputs: &[TxInTemplate::Bogus],
+                    outputs: &[TxOutTemplate::new(10_000, None)],
+                    last_seen: Some(1),
+                    ..Default::default()
+                },
+                TxTemplate {
+                    tx_name: "S1",
+                    inputs: &[TxInTemplate::PrevTx("A", 0)],
+                    outputs: &[TxOutTemplate::new(9_000, None)],
+                    last_seen: Some(2),
+                    ..Default::default()
+                },
+                TxTemplate {
+                    tx_name: "S2",
+                    inputs: &[TxInTemplate::PrevTx("A", 0), TxInTemplate::PrevTx("S1", 0)],
+                    outputs: &[TxOutTemplate::new(17_000, None)],
+                    last_seen: Some(3),
+                    ..Default::default()
+                },
+            ],
+            exp_chain_txs: HashSet::from(["A", "S1"]),
+            exp_chain_txouts: HashSet::from([]),
+            exp_unspents: HashSet::from([]),
+            exp_balance: Balance::default(),
+        },
+        Scenario {
+            name: "tx spends from 2 conflicting transactions where the conflict is nested",
+            tx_templates: &[
+                TxTemplate {
+                    tx_name: "A",
+                    inputs: &[TxInTemplate::Bogus],
+                    outputs: &[TxOutTemplate::new(10_000, Some(0))],
+                    last_seen: Some(1),
+                    ..Default::default()
+                },
+                TxTemplate {
+                    tx_name: "S1",
+                    inputs: &[TxInTemplate::PrevTx("A", 0)],
+                    outputs: &[TxOutTemplate::new(9_000, Some(0))],
+                    last_seen: Some(3),
+                    ..Default::default()
+                },
+                TxTemplate {
+                    tx_name: "B",
+                    inputs: &[TxInTemplate::PrevTx("S1", 0)],
+                    outputs: &[TxOutTemplate::new(8_000, Some(0))],
+                    last_seen: Some(2),
+                    ..Default::default()
+                },
+                TxTemplate {
+                    tx_name: "S2",
+                    inputs: &[TxInTemplate::PrevTx("B", 0), TxInTemplate::PrevTx("A", 0)],
+                    outputs: &[TxOutTemplate::new(17_000, Some(0))],
+                    last_seen: Some(4),
+                    ..Default::default()
+                },
+            ],
+            exp_chain_txs: HashSet::from(["A", "S1", "B"]),
+            exp_chain_txouts: HashSet::from([("A", 0), ("B", 0), ("S1", 0)]),
+            exp_unspents: HashSet::from([("B", 0)]),
+            exp_balance: Balance { trusted_pending: Amount::from_sat(8_000), ..Default::default() },
+        },
+        Scenario {
+            name: "tx spends from 2 conflicting transactions where the conflict is nested (different last_seens)",
+            tx_templates: &[
+                TxTemplate {
+                    tx_name: "A",
+                    inputs: &[TxInTemplate::Bogus],
+                    outputs: &[TxOutTemplate::new(10_000, Some(0))],
+                    last_seen: Some(1),
+                    ..Default::default()
+                },
+                TxTemplate {
+                    tx_name: "S1",
+                    inputs: &[TxInTemplate::PrevTx("A", 0)],
+                    outputs: &[TxOutTemplate::new(9_000, Some(0))],
+                    last_seen: Some(4),
+                    ..Default::default()
+                },
+                TxTemplate {
+                    tx_name: "B",
+                    inputs: &[TxInTemplate::PrevTx("S1", 0)],
+                    outputs: &[TxOutTemplate::new(8_000, Some(0))],
+                    last_seen: Some(2),
+                    ..Default::default()
+                },
+                TxTemplate {
+                    tx_name: "S2",
+                    inputs: &[TxInTemplate::PrevTx("A", 0), TxInTemplate::PrevTx("B", 0)],
+                    outputs: &[TxOutTemplate::new(17_000, Some(0))],
+                    last_seen: Some(3),
+                    ..Default::default()
+                },
+            ],
+            exp_chain_txs: HashSet::from(["A", "S1", "B"]),
+            exp_chain_txouts: HashSet::from([("A", 0), ("B", 0), ("S1", 0)]),
+            exp_unspents: HashSet::from([("B", 0)]),
+            exp_balance: Balance { trusted_pending: Amount::from_sat(8_000), ..Default::default() },
+        },
     ];
 
     for scenario in scenarios {
```
