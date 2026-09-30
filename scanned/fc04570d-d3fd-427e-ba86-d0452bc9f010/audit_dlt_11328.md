# [?] fix: Non-determinism from under constrained checks (#6945)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-01-04
Source: https://github.com/noir-lang/noir/commit/203242c0c05e9333caaa8df55a4ed9a02e000882
Type: security-commit

## Details
fix: Non-determinism from under constrained checks (#6945)

## Patch
### compiler/noirc_evaluator/src/ssa/checks/check_for_underconstrained_values.rs
```diff
@@ -10,7 +10,7 @@ use crate::ssa::ir::value::{Value, ValueId};
 use crate::ssa::ssa_gen::Ssa;
 use im::HashMap;
 use rayon::prelude::*;
-use std::collections::{BTreeMap, HashSet};
+use std::collections::{BTreeMap, BTreeSet, HashSet};
 use tracing::trace;
 
 impl Ssa {
@@ -73,15 +73,15 @@ fn check_for_underconstrained_values_within_function(
 
     context.compute_sets_of_connected_value_ids(function, all_functions);
 
-    let all_brillig_generated_values: HashSet<ValueId> =
+    let all_brillig_generated_values: BTreeSet<ValueId> =
         context.brillig_return_to_argument.keys().copied().collect();
 
     let connected_sets_indices =
         context.find_sets_connected_to_function_inputs_or_outputs(function);
 
     // Go through each disconnected set, find brillig calls that caused it and form warnings
     for set_index in
-        HashSet::from_iter(0..(context.value_sets.len())).difference(&connected_sets_indices)
+        BTreeSet::from_iter(0..(context.value_sets.len())).difference(&connected_sets_indices)
     {
         let current_set = &context.value_sets[*set_index];
         warnings.append(&mut context.find_disconnecting_brillig_calls_with_results_in_set(
@@ -104,7 +104,7 @@ struct DependencyContext {
     array_elements: HashMap<ValueId, ValueId>,
     // Map of brillig call ids to sets of the value ids descending
     // from their arguments and results
-    tainted: HashMap<InstructionId, BrilligTaintedIds>,
+    tainted: BTreeMap<InstructionId, BrilligTaintedIds>,
 }
 
 /// Structure keeping track of value ids descending from Brillig calls'
@@ -434,7 +434,7 @@ impl DependencyContext {
 struct Context {
     visited_blocks: HashSet<BasicBlockId>,
     block_queue: Vec<BasicBlockId>,
-    value_sets: Vec<HashSet<ValueId>>,
+    value_sets: Vec<BTreeSet<ValueId>>,
     brillig_return_to_argument: HashMap<ValueId, Vec<ValueId>>,
     brillig_return_to_instruction_id: HashMap<ValueId, InstructionId>,
 }
@@ -467,15 +467,15 @@ impl Context {
     fn find_sets_connected_to_function_inputs_or_outputs(
         &mut self,
         function: &Function,
-    ) -> HashSet<usize> {
+    ) -> BTreeSet<usize> {
         let variable_parameters_and_return_values = function
             .parameters()
             .iter()
             .chain(function.returns())
             .filter(|id| function.dfg.get_numeric_constant(**id).is_none())
             .map(|value_id| function.dfg.resolve(*value_id));
 
-        let mut connected_sets_indices: HashSet<usize> = HashSet::new();
+        let mut connected_sets_indices: BTreeSet<usize> = BTreeSet::default();
 
         // Go through each parameter and each set and check if the set contains the parameter
         // If it's the case, then that set doesn't present an issue
@@ -492,8 +492,8 @@ impl Context {
     /// Find which Brillig calls separate this set from others and return bug warnings about them
     fn find_disconnecting_brillig_calls_with_results_in_set(
         &self,
-        current_set: &HashSet<ValueId>,
-        all_brillig_generated_values: &HashSet<ValueId>,
+        current_set: &BTreeSet<ValueId>,
+        all_brillig_generated_values: &BTreeSet<ValueId>,
         function: &Function,
     ) -> Vec<SsaReport> {
         let mut warnings = Vec::new();
@@ -503,7 +503,7 @@ impl Context {
         // Go through all Brillig outputs in the set
         for brillig_output_in_set in intersection {
             // Get the inputs that correspond to the output
-            let inputs: HashSet<ValueId> =
+            let inputs: BTreeSet<ValueId> =
                 self.brillig_return_to_argument[&brillig_output_in_set].iter().copied().collect();
 
             // Check if any of them are not in the set
@@ -532,7 +532,7 @@ impl Context {
         let instructions = function.dfg[block].instructions();
 
         for instruction in instructions.iter() {
-            let mut instruction_arguments_and_results = HashSet::new();
+            let mut instruction_arguments_and_results = BTreeSet::new();
 
             // Insert non-constant instruction arguments
             function.dfg[*instruction].for_each_value(|value_id| {
@@ -638,15 +638,15 @@ impl Context {
     /// Merge all small sets into larger ones based on whether the sets intersect or not
     ///
     /// If two small sets have a common ValueId, we merge them into one
-    fn merge_sets(current: &[HashSet<ValueId>]) -> Vec<HashSet<ValueId>> {
+    fn merge_sets(current: &[BTreeSet<ValueId>]) -> Vec<BTreeSet<ValueId>> {
         let mut new_set_id: usize = 0;
-        let mut updated_sets: HashMap<usize, HashSet<ValueId>> = HashMap::new();
-        let mut value_dictionary: HashMap<ValueId, usize> = HashMap::new();
-        let mut parsed_value_set: HashSet<ValueId> = HashSet::new();
+        let mut updated_sets: BTreeMap<usize, BTreeSet<ValueId>> = BTreeMap::default();
+        let mut value_dictionary: HashMap<ValueId, usize> = HashMap::default();
+        let mut parsed_value_set: BTreeSet<ValueId> = BTreeSet::default();
 
         for set in current.iter() {
             // Check if the set has any of the ValueIds we've encountered at previous iterations
-            let intersection: HashSet<ValueId> =
+            let intersection: BTreeSet<ValueId> =
                 set.intersection(&parsed_value_set).copied().collect();
             parsed_value_set.extend(set.iter());
 
@@ -663,7 +663,7 @@ impl Context {
             }
 
             // If there is an intersection, we have to join the sets
-            let mut joining_sets_ids: HashSet<usize> =
+            let mut joining_sets_ids: BTreeSet<usize> =
                 intersection.iter().map(|x| value_dictionary[x]).collect();
             let mut largest_set_size = usize::MIN;
             let mut largest_set_index = usize::MAX;
@@ -677,7 +677,7 @@ impl Context {
             joining_sets_ids.remove(&largest_set_index);
 
             let mut largest_set =
-                updated_sets.extract(&largest_set_index).expect("Set should be in the hashmap").0;
+                updated_sets.remove(&largest_set_index).expect("Set should be in the hashmap");
 
             // For each of other sets that need to be joined
             for set_id in joining_sets_ids.iter() {
@@ -702,7 +702,7 @@ impl Context {
 
     /// Parallel version of merge_sets
     /// The sets are merged by chunks, and then the chunks are merged together
-    fn merge_sets_par(sets: &[HashSet<ValueId>]) -> Vec<HashSet<ValueId>> {
+    fn merge_sets_par(sets: &[BTreeSet<ValueId>]) -> Vec<BTreeSet<ValueId>> {
         let mut sets = sets.to_owned();
         let mut len = sets.len();
         let mut prev_len = len + 1;
```

### tooling/nargo_cli/build.rs
```diff
@@ -208,6 +208,7 @@ fn test_{test_name}(force_brillig: ForceBrillig, inliner_aggressiveness: Inliner
     nargo.arg("--program-dir").arg(test_program_dir);
     nargo.arg("{test_command}").arg("--force");
     nargo.arg("--inliner-aggressiveness").arg(inliner_aggressiveness.0.to_string());
+    nargo.arg("--check-non-determinism");
 
     if force_brillig.0 {{
         nargo.arg("--force-brillig");
@@ -217,7 +218,6 @@ fn test_{test_name}(force_brillig: ForceBrillig, inliner_aggressiveness: Inliner
         nargo.arg("50");
 
         // Check whether the test case is non-deterministic
-        nargo.arg("--check-non-determinism");
     }}
 
     {test_content}
```
