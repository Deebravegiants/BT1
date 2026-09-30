# [?] Fix register allocator non-deterministic output across platforms (#7422)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2025-09-30
Source: https://github.com/FuelLabs/sway/commit/be932cc1b940d1a0d9b9341600e8e0d81f6ad337
Type: security-commit

## Details
Fix register allocator non-deterministic output across platforms (#7422)

[Make spill slot assignment deterministic across
platforms](https://github.com/FuelLabs/sway/commit/d7c4072e910e2d0827236d2adbb7471a6ddc4264)

Pick spill candidates with a stable tie-break so every host spills the
same virtual register.

Sort the spill set before handing out stack slots to keep offsets
consistent.

Closes https://github.com/FuelLabs/sway/issues/7390.

## Checklist

- [x] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [x] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] If my change requires substantial documentation changes, I have
[requested support from the DevRel
team](https://github.com/FuelLabs/devrel-requests/issues/new/choose)
- [x] I have added tests that prove my fix is effective or that my
feature works.
- [x] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

## Patch
### sway-core/src/asm_generation/fuel/register_allocator.rs
```diff
@@ -14,6 +14,7 @@ use petgraph::{
     Direction::{Incoming, Outgoing},
 };
 use rustc_hash::{FxHashMap, FxHashSet};
+use std::cmp::Ordering;
 use std::collections::{hash_map, BTreeSet, HashMap};
 use sway_error::error::CompileError;
 use sway_ir::size_bytes_round_up_to_word_alignment;
@@ -498,13 +499,26 @@ pub(crate) fn color_interference_graph(
             }
         }
 
-        if let Some(&spill_reg_index) = pending.iter().max_by(|&&node1, &&node2| {
-            // At the moment, our spill priority function is just this,
-            // i.e., spill the register with more incoming interferences.
-            // (roughly indicating how long the interval is).
-            get_connected_incoming_neighbors(interference_graph, node1)
-                .count()
-                .cmp(&get_connected_incoming_neighbors(interference_graph, node2).count())
+        // At the moment, our spill priority function is just this,
+        // i.e., spill the register with more incoming interferences.
+        // (roughly indicating how long the interval is).
+        if let Some(spill_reg_index) = pending.iter().copied().max_by(|node1, node2| {
+            let node1_priority =
+                get_connected_incoming_neighbors(interference_graph, *node1).count();
+            let node2_priority =
+                get_connected_incoming_neighbors(interference_graph, *node2).count();
+            match node1_priority.cmp(&node2_priority) {
+                Ordering::Equal => {
+                    // Equal priorities are broken deterministically and do not alter the spill heuristic.
+                    let reg_cmp = interference_graph[*node1].cmp(&interference_graph[*node2]);
+                    if reg_cmp == Ordering::Equal {
+                        node1.index().cmp(&node2.index())
+                    } else {
+                        reg_cmp
+                    }
+                }
+                other => other,
+            }
         }) {
             let spill_reg = interference_graph[spill_reg_index].clone();
             spills.insert(spill_reg.clone());
@@ -740,11 +754,7 @@ fn spill(ops: &[Op], spills: &FxHashSet<VirtualRegister>) -> Vec<Op> {
     let locals_size_bytes = size_bytes_round_up_to_word_alignment!(locals_size_bytes);
 
     // Determine the stack slots for each spilled register.
-    let spill_offsets_bytes: FxHashMap<VirtualRegister, u32> = spills
-        .iter()
-        .enumerate()
-        .map(|(i, reg)| (reg.clone(), (i * 8) as u32 + locals_size_bytes))
-        .collect();
+    let spill_offsets_bytes = spill_offsets(spills, locals_size_bytes);
 
     let spills_size = (8 * spills.len()) as u32;
     let new_locals_byte_size = locals_size_bytes + spills_size;
@@ -952,3 +962,58 @@ fn spill(ops: &[Op], spills: &FxHashSet<VirtualRegister>) -> Vec<Op> {
 
     spilled
 }
+
+fn spill_offsets(
+    spills: &FxHashSet<VirtualRegister>,
+    locals_size_bytes: u32,
+) -> FxHashMap<VirtualRegister, u32> {
+    let mut spill_regs: Vec<_> = spills.iter().collect();
+    spill_regs.sort();
+    spill_regs
+        .into_iter()
+        .enumerate()
+        .map(|(i, reg)| (reg.clone(), (i * 8) as u32 + locals_size_bytes))
+        .collect()
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use rustc_hash::FxHashSet;
+
+    fn make_reg(name: &str) -> VirtualRegister {
+        VirtualRegister::Virtual(name.to_owned())
+    }
+
+    #[test]
+    fn spill_offsets_are_deterministic() {
+        let locals_size_bytes = 24u32;
+
+        let mut set_a = FxHashSet::default();
+        set_a.insert(make_reg("r1"));
+        set_a.insert(make_reg("r2"));
+        set_a.insert(make_reg("r3"));
+
+        let mut set_b = FxHashSet::default();
+        set_b.insert(make_reg("r3"));
+        set_b.insert(make_reg("r1"));
+        set_b.insert(make_reg("r2"));
+
+        let offsets_a = spill_offsets(&set_a, locals_size_bytes);
+        let offsets_b = spill_offsets(&set_b, locals_size_bytes);
+
+        assert_eq!(offsets_a, offsets_b);
+
+        let mut sorted: Vec<_> = offsets_a.into_iter().collect();
+        sorted.sort_by(|(reg_l, _), (reg_r, _)| reg_l.cmp(reg_r));
+        assert_eq!(
+            sorted,
+            vec![
+                (make_reg("r1"), locals_size_bytes),
+                (make_reg("r2"), locals_size_bytes + 8),
+                (make_reg("r3"), locals_size_bytes + 16),
+            ]
+        );
+        assert_eq!(offsets_b.len(), 3);
+    }
+}
```
