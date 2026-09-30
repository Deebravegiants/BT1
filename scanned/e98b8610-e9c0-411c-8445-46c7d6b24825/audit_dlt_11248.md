# [?] fix(ssa_fuzzer): fix non-deterministic iteration order (#12041)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-03-30
Source: https://github.com/noir-lang/noir/commit/4bcbec9af3684b02b2571fdf8d40afd844a64a31
Type: security-commit

## Details
fix(ssa_fuzzer): fix non-deterministic iteration order (#12041)

## Patch
### tooling/ssa_fuzzer/fuzzer/src/fuzz_lib/block_context.rs
```diff
@@ -8,14 +8,14 @@ use super::{
 use noir_ssa_fuzzer::builder::{FuzzerBuilder, InstructionWithOneArg, InstructionWithTwoArgs};
 use noir_ssa_fuzzer::typed_value::{NumericType, Point, Scalar, Type, TypedValue};
 use noirc_evaluator::ssa::ir::{basic_block::BasicBlockId, function::Function, map::Id};
-use std::collections::{HashMap, VecDeque};
+use std::collections::{BTreeMap, VecDeque};
 
 /// Main context for the ssa block containing both ACIR and Brillig builders and their state
 /// It works with indices of variables Ids, because it cannot handle Ids logic for ACIR and Brillig
 #[derive(Debug, Clone)]
 pub(crate) struct BlockContext {
     /// Ids of the Program variables stored as TypedValue separated by type
-    pub(crate) stored_variables: HashMap<Type, Vec<TypedValue>>,
+    pub(crate) stored_variables: BTreeMap<Type, Vec<TypedValue>>,
     /// Parent blocks history
     pub(crate) parent_blocks_history: VecDeque<BasicBlockId>,
     /// Children blocks
@@ -26,7 +26,7 @@ pub(crate) struct BlockContext {
 
 impl BlockContext {
     pub(crate) fn new(
-        stored_variables: HashMap<Type, Vec<TypedValue>>,
+        stored_variables: BTreeMap<Type, Vec<TypedValue>>,
         parent_blocks_history: VecDeque<BasicBlockId>,
         options: SsaBlockOptions,
     ) -> Self {
```

### tooling/ssa_fuzzer/fuzzer/src/fuzz_lib/function_context.rs
```diff
@@ -14,7 +14,7 @@ use noir_ssa_fuzzer::{
 use noirc_evaluator::ssa::ir::{basic_block::BasicBlockId, function::Function, map::Id};
 use serde::{Deserialize, Serialize};
 use std::{
-    collections::{BTreeMap, HashMap, HashSet, VecDeque},
+    collections::{BTreeMap, HashSet, VecDeque},
     hash::Hash,
 };
 use strum_macros::EnumCount;
@@ -108,9 +108,9 @@ pub(crate) struct FuzzerFunctionContext<'a> {
     /// Instruction blocks
     instruction_blocks: &'a Vec<InstructionBlock>,
     /// Hashmap of stored variables in blocks
-    stored_variables_for_block: HashMap<BasicBlockId, HashMap<Type, Vec<TypedValue>>>,
+    stored_variables_for_block: BTreeMap<BasicBlockId, BTreeMap<Type, Vec<TypedValue>>>,
     /// Hashmap of stored blocks
-    stored_blocks: HashMap<BasicBlockId, StoredBlock>,
+    stored_blocks: BTreeMap<BasicBlockId, StoredBlock>,
     /// Options of the program context
     function_context_options: FunctionContextOptions,
     /// Number of instructions inserted in the program
@@ -119,7 +119,7 @@ pub(crate) struct FuzzerFunctionContext<'a> {
     inserted_ssa_blocks_count: usize,
 
     /// Stored cycles info, to handle loops in Jmp, JmpIf and finalization
-    cycle_bodies_to_iters_ids: HashMap<BasicBlockId, CycleInfo>,
+    cycle_bodies_to_iters_ids: BTreeMap<BasicBlockId, CycleInfo>,
     /// Number of iterations of loops in the program
     parent_iterations_count: usize,
 
@@ -138,7 +138,7 @@ impl<'a> FuzzerFunctionContext<'a> {
         defined_functions: BTreeMap<Id<Function>, FunctionInfo>,
         builder: &'a mut FuzzerBuilder,
     ) -> Self {
-        let mut ids = HashMap::new();
+        let mut ids = BTreeMap::new();
         for type_ in types {
             let id = builder.insert_variable(type_.clone().into());
             ids.entry(type_.clone()).or_insert(Vec::new()).push(id);
@@ -159,12 +159,12 @@ impl<'a> FuzzerFunctionContext<'a> {
             current_block,
             not_terminated_blocks: VecDeque::new(),
             instruction_blocks,
-            stored_variables_for_block: HashMap::new(),
-            stored_blocks: HashMap::new(),
+            stored_variables_for_block: BTreeMap::new(),
+            stored_blocks: BTreeMap::new(),
             function_context_options: context_options,
             inserted_instructions_count: 0,
             inserted_ssa_blocks_count: 0,
-            cycle_bodies_to_iters_ids: HashMap::new(),
+            cycle_bodies_to_iters_ids: BTreeMap::new(),
             parent_iterations_count: 1,
             defined_functions,
             return_type,
@@ -182,7 +182,7 @@ impl<'a> FuzzerFunctionContext<'a> {
         defined_functions: BTreeMap<Id<Function>, FunctionInfo>,
         builder: &'a mut FuzzerBuilder,
     ) -> Self {
-        let mut ids = HashMap::new();
+        let mut ids = BTreeMap::new();
 
         for (value, type_) in values_types {
             let field_element = value;
@@ -206,12 +206,12 @@ impl<'a> FuzzerFunctionContext<'a> {
             current_block,
             not_terminated_blocks: VecDeque::new(),
             instruction_blocks,
-            stored_variables_for_block: HashMap::new(),
-            stored_blocks: HashMap::new(),
+            stored_variables_for_block: BTreeMap::new(),
+            stored_blocks: BTreeMap::new(),
             function_context_options: context_options,
             inserted_instructions_count: 0,
             inserted_ssa_blocks_count: 0,
-            cycle_bodies_to_iters_ids: HashMap::new(),
+            cycle_bodies_to_iters_ids: BTreeMap::new(),
             parent_iterations_count: 1,
             defined_functions,
             return_type,
```

### tooling/ssa_fuzzer/src/typed_value.rs
```diff
@@ -7,7 +7,20 @@ use serde::{Deserialize, Serialize};
 use std::sync::Arc;
 use strum_macros::EnumCount;
 
-#[derive(Arbitrary, Debug, Clone, PartialEq, Eq, Hash, Copy, Serialize, Deserialize, EnumCount)]
+#[derive(
+    Arbitrary,
+    Debug,
+    Clone,
+    PartialEq,
+    Eq,
+    PartialOrd,
+    Ord,
+    Hash,
+    Copy,
+    Serialize,
+    Deserialize,
+    EnumCount,
+)]
 pub enum NumericType {
     Field,
     Boolean,
@@ -59,7 +72,9 @@ impl From<NumericType> for SsaNumericType {
     }
 }
 
-#[derive(Arbitrary, Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize, EnumCount)]
+#[derive(
+    Arbitrary, Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize, EnumCount,
+)]
 pub enum Type {
     Numeric(NumericType),
     Reference(Arc<Type>),
```
