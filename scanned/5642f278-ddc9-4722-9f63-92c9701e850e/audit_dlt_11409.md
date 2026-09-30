# [?] fix advice non deterministic problem

## Summary
Severity: Unknown
Chain: ZK
Component: scroll-tech/zkevm-circuits
Published: 2023-04-26
Source: https://github.com/scroll-tech/zkevm-circuits/commit/7e821a9386e6c9aad85ef40e669986305e04dc77
Type: security-commit

## Details
fix advice non deterministic problem

## Patch
### zkevm-circuits/src/copy_circuit.rs
```diff
@@ -24,7 +24,7 @@ use halo2_proofs::{
     poly::Rotation,
 };
 use itertools::Itertools;
-use std::{collections::HashMap, marker::PhantomData};
+use std::{collections::BTreeMap, marker::PhantomData};
 
 #[cfg(feature = "onephase")]
 use halo2_proofs::plonk::FirstPhase as SecondPhase;
@@ -735,7 +735,7 @@ pub struct ExternalData {
     /// StateCircuit -> rws
     pub rws: RwMap,
     /// BytecodeCircuit -> bytecodes
-    pub bytecodes: HashMap<Word, Bytecode>,
+    pub bytecodes: BTreeMap<Word, Bytecode>,
 }
 
 /// Copy Circuit
```

### zkevm-circuits/src/witness/block.rs
```diff
@@ -1,5 +1,5 @@
 use ethers_core::types::Signature;
-use std::collections::{BTreeMap, HashMap};
+use std::collections::BTreeMap;
 
 #[cfg(any(feature = "test", test))]
 use crate::evm_circuit::{detect_fixed_table_tags, EvmCircuit};
@@ -46,7 +46,7 @@ pub struct Block<F> {
     /// Read write events in the RwTable
     pub rws: RwMap,
     /// Bytecode used in the block
-    pub bytecodes: HashMap<Word, Bytecode>,
+    pub bytecodes: BTreeMap<Word, Bytecode>,
     /// The block context
     pub context: BlockContexts,
     /// The init state of mpt
```
