# [?] fix(mem2reg): Remove possibility of underflow (#6107)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-09-19
Source: https://github.com/noir-lang/noir/commit/aea5cc789ccf4a4d16b1d238d99474f37920b37e
Type: security-commit

## Details
fix(mem2reg): Remove possibility of underflow (#6107)

# Description

## Problem\*

Resolves ICE ran into by @asterite 

## Summary\*

After #5925 we have a couple counters that both increment and decrement.
In theory they are never supposed to underflow. @asterite has discovered
a bug with the remaining last stores counter. I would like to implement
the remaining last stores removal in a better way that removes the need
for this counter to be decremented, but for now I just block if by check
we are not decrementing zero.

## Additional Context



## Documentation\*

Check one:
- [X] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [X] I have tested the changes locally.
- [X] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

---------

Co-authored-by: jfecher <jake@aztecprotocol.com>

## Patch
### compiler/noirc_evaluator/src/ssa/opt/mem2reg.rs
```diff
@@ -288,6 +288,8 @@ impl<'f> PerFunctionContext<'f> {
             .filter(|param| self.inserter.function.dfg.value_is_reference(**param))
             .collect::<BTreeSet<_>>();
 
+        // Must collect here as we are immutably borrowing `self` to fetch the reference parameters
+        let mut values_to_reduce_counts = Vec::new();
         for (allocation, instruction) in &references.last_stores {
             if let Some(expression) = references.expressions.get(allocation) {
                 if let Some(aliases) = references.aliases.get(expression) {
@@ -297,13 +299,15 @@ impl<'f> PerFunctionContext<'f> {
                     // If `allocation_aliases_parameter` is known to be false
                     if allocation_aliases_parameter == Some(false) {
                         self.instructions_to_remove.insert(*instruction);
-                        if let Some(context) = self.load_results.get_mut(allocation) {
-                            context.uses -= 1;
-                        }
+                        values_to_reduce_counts.push(*allocation);
                     }
                 }
             }
         }
+
+        for value in values_to_reduce_counts {
+            self.reduce_load_result_count(value);
+        }
     }
 
     fn increase_load_ref_counts(&mut self, value: ValueId) {
@@ -406,25 +410,17 @@ impl<'f> PerFunctionContext<'f> {
                     else {
                         panic!("Should have a store instruction here");
                     };
-                    if let Some(context) = self.load_results.get_mut(&address) {
-                        context.uses -= 1;
-                    }
-                    if let Some(context) = self.load_results.get_mut(&value) {
-                        context.uses -= 1;
-                    }
+                    self.reduce_load_result_count(address);
+                    self.reduce_load_result_count(value);
                 }
 
                 let known_value = references.get_known_value(value);
                 if let Some(known_value) = known_value {
                     let known_value_is_address = known_value == address;
                     if known_value_is_address {
                         self.instructions_to_remove.insert(instruction);
-                        if let Some(context) = self.load_results.get_mut(&address) {
-                            context.uses -= 1;
-                        }
-                        if let Some(context) = self.load_results.get_mut(&value) {
-                            context.uses -= 1;
-                        }
+                        self.reduce_load_result_count(address);
+                        self.reduce_load_result_count(value);
                     } else {
                         references.last_stores.insert(address, instruction);
                     }
@@ -617,6 +613,12 @@ impl<'f> PerFunctionContext<'f> {
         }
     }
 
+    fn reduce_load_result_count(&mut self, value: ValueId) {
+        if let Some(context) = self.load_results.get_mut(&value) {
+            context.uses = context.uses.saturating_sub(1);
+        }
+    }
+
     fn recursively_add_values(&self, value: ValueId, set: &mut HashSet<ValueId>) {
         set.insert(value);
         if let Some((elements, _)) = self.inserter.function.dfg.get_array_constant(value) {
@@ -741,7 +743,7 @@ impl<'f> PerFunctionContext<'f> {
                 if all_loads_removed && !store_alias_used {
                     self.instructions_to_remove.insert(*store_instruction);
                     if let Some((_, counter)) = remaining_last_stores.get_mut(store_address) {
-                        *counter -= 1;
+                        *counter = counter.saturating_sub(1);
                     }
                 } else if let Some((_, counter)) = remaining_last_stores.get_mut(store_address) {
                     *counter += 1;
```
