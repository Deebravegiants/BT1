# [?] fix nondeterministic constraint generation (#1706)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2024-02-22
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/272377570706e14745aa22573a29e8270d085bae
Type: security-commit

## Details
fix nondeterministic constraint generation (#1706)

### Description

Change HashMap to BTreeMap in memory.rs and in cell_placement_strategy.

### Issue Link

#1700

### Type of change

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing
functionality to not work as expected)
- [ ] This change requires a documentation update

### Contents

- fix in memory.rs
- fix in cell_placement_strategy

### Rationale

Generates different circuit keys making proof verification fail for
different witnesses.

### How Has This Been Tested?

Manual testing.

## Patch
### zkevm-circuits/src/circuit_tools/memory.rs
```diff
@@ -7,7 +7,7 @@ use halo2_proofs::{
     poly::Rotation,
 };
 use std::{
-    collections::HashMap,
+    collections::BTreeMap,
     marker::PhantomData,
     ops::{Index, IndexMut},
 };
@@ -20,7 +20,7 @@ use super::{
 
 #[derive(Clone, Debug, Default)]
 pub(crate) struct Memory<F: Field, C: CellType, MB: MemoryBank<F, C>> {
-    banks: HashMap<C, MB>,
+    banks: BTreeMap<C, MB>,
     _phantom: PhantomData<F>,
     tag_counter: usize,
 }
@@ -42,7 +42,7 @@ impl<F: Field, C: CellType, MB: MemoryBank<F, C>> IndexMut<C> for Memory<F, C, M
 impl<F: Field, C: CellType, MB: MemoryBank<F, C>> Memory<F, C, MB> {
     pub(crate) fn new() -> Self {
         Self {
-            banks: HashMap::new(),
+            banks: BTreeMap::new(),
             _phantom: PhantomData,
             tag_counter: 0,
         }
```

### zkevm-circuits/src/mpt_circuit.rs
```diff
@@ -766,10 +766,38 @@ pub fn load_proof_from_file(path: &str) -> Vec<Node> {
 mod tests {
     use super::*;
     use halo2_proofs::{dev::MockProver, halo2curves::bn256::Fr};
-    use std::{fs, ops::Deref};
+    use itertools::Itertools;
+    use std::{fs, ops::Deref, path::PathBuf};
 
     #[test]
     fn test_mpt() {
+        let degree = 15;
+        get_witnesses()
+            .enumerate()
+            .for_each(|(idx, (path, num_rows, circuit))| {
+                println!("{} {:?}", idx, path);
+                let prover = MockProver::<Fr>::run(degree, &circuit, vec![]).unwrap();
+                assert_eq!(prover.verify_at_rows(0..num_rows, 0..num_rows,), Ok(()));
+                // assert_eq!(prover.verify_par(), Ok(()));
+                // prover.assert_satisfied();
+            });
+    }
+
+    #[test]
+    fn variadic_size_check() {
+        let mut circuits = get_witnesses();
+        let first = circuits.next().unwrap().2;
+        let second = circuits.next().unwrap().2;
+
+        let degree = 15;
+        let prover_1 = MockProver::<Fr>::run(degree, &first, vec![]).unwrap();
+        let prover_2 = MockProver::<Fr>::run(degree, &second, vec![]).unwrap();
+
+        assert_eq!(prover_1.fixed(), prover_2.fixed());
+        assert_eq!(prover_1.permutation(), prover_2.permutation());
+    }
+
+    fn get_witnesses() -> impl Iterator<Item = (PathBuf, usize, MPTCircuit<Fr>)> {
         let path = "src/mpt_circuit/tests";
         let files = fs::read_dir(path).unwrap();
         files
@@ -781,8 +809,8 @@ mod tests {
                     false
                 }
             })
-            .enumerate()
-            .for_each(|(idx, f)| {
+            .sorted_by(|a, b| a.file_name().cmp(&b.file_name()))
+            .map(|f| {
                 let path = f.path();
                 let mut parts = path.to_str().unwrap().split('-');
                 parts.next();
@@ -796,24 +824,21 @@ mod tests {
                         keccak_data.push(k.deref().clone());
                     }
                 }
-
                 let disable_preimage_check = nodes[0].start.clone().unwrap().disable_preimage_check;
                 let degree = 15;
                 let max_nodes = 520;
-                let circuit = MPTCircuit::<Fr> {
-                    nodes,
-                    keccak_data,
-                    degree,
-                    max_nodes,
-                    disable_preimage_check,
-                    _marker: PhantomData,
-                };
-
-                println!("{} {:?}", idx, path);
-                let prover = MockProver::<Fr>::run(degree as u32, &circuit, vec![]).unwrap();
-                assert_eq!(prover.verify_at_rows(0..num_rows, 0..num_rows,), Ok(()));
-                // assert_eq!(prover.verify(), Ok(()));
-                // prover.assert_satisfied();
-            });
+                (
+                    path,
+                    num_rows,
+                    MPTCircuit::<Fr> {
+                        nodes,
+                        keccak_data,
+                        degree,
+                        max_nodes,
+                        disable_preimage_check,
+                        _marker: PhantomData,
+                    },
+                )
+            })
     }
 }
```

### zkevm-circuits/src/util/cell_placement_strategy.rs
```diff
@@ -1,4 +1,4 @@
-use std::collections::{BTreeMap, HashMap};
+use std::collections::BTreeMap;
 
 use eth_types::Field;
 use halo2_proofs::plonk::{Advice, Column, ConstraintSystem};
@@ -8,7 +8,7 @@ use super::cell_manager::{
 };
 
 #[derive(Clone, Debug, Default)]
-pub(crate) struct CMFixedWidthStrategyDistribution(HashMap<CellType, Vec<Column<Advice>>>);
+pub(crate) struct CMFixedWidthStrategyDistribution(BTreeMap<CellType, Vec<Column<Advice>>>);
 
 impl CMFixedWidthStrategyDistribution {
     pub(crate) fn add(&mut self, cell_type: CellType, advice: Column<Advice>) {
@@ -34,7 +34,7 @@ pub(crate) struct CMFixedWidthStrategy {
     advices: CMFixedWidthStrategyDistribution,
     height_offset: usize,
 
-    next: HashMap<CellType, (usize, usize)>,
+    next: BTreeMap<CellType, (usize, usize)>,
 
     perm_substitution: bool,
     max_height: usize,
@@ -52,7 +52,7 @@ impl CMFixedWidthStrategy {
         CMFixedWidthStrategy {
             advices,
             height_offset,
-            next: HashMap::default(),
+            next: BTreeMap::default(),
             perm_substitution: false,
             max_height: usize::max_value(),
         }
```
