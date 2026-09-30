# [?] fix: remove most blackbox panics (#11136)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-08
Source: https://github.com/noir-lang/noir/commit/78a54455147d9ddbec669e78ebd107aed5245111
Type: security-commit

## Details
fix: remove most blackbox panics (#11136)

Co-authored-by: Michael J Klein <michaeljklein@users.noreply.github.com>

## Patch
### compiler/noirc_evaluator/src/ssa/opt/remove_if_else.rs
```diff
@@ -107,6 +107,7 @@ use crate::errors::RtResult;
 
 use crate::ssa::ir::dfg::simplify::value_merger::ValueMerger;
 use crate::ssa::ir::types::NumericType;
+use crate::ssa::opt::simple_optimization::SimpleOptimizationContext;
 use crate::ssa::{
     Ssa,
     ir::{
@@ -241,28 +242,10 @@ impl Context {
 
                         self.vector_constant_size_override(context.dfg, intrinsic, arguments);
 
-                        match self.vector_capacity_change(
-                            context.dfg,
-                            intrinsic,
-                            arguments,
-                            results,
-                        ) {
-                            SizeChange::None => (),
-                            SizeChange::SetTo { old, new } => {
-                                self.set_capacity(context.dfg, old, new, |c| c);
-                            }
-                            SizeChange::Inc { old, new } => {
-                                self.set_capacity(context.dfg, old, new, |c| {
-                                    // Checked addition because increasing the capacity must increase it (cannot wrap around or saturate).
-                                    c.checked_add(1).expect("Vector capacity overflow")
-                                });
-                            }
-                            SizeChange::Dec { old, new } => {
-                                // We use a saturating sub here as calling `pop_front` or `pop_back` on a zero-length vector
-                                // would otherwise underflow.
-                                self.set_capacity(context.dfg, old, new, |c| c.saturating_sub(1));
-                            }
-                        }
+                        let size_change =
+                            self.vector_capacity_change(context.dfg, intrinsic, arguments, results);
+
+                        self.change_size(size_change, context);
                     }
                 }
                 // Track vector sizes through array set instructions
@@ -276,6 +259,31 @@ impl Context {
         })
     }
 
+    fn change_size(&mut self, size_change: SizeChange, context: &mut SimpleOptimizationContext) {
+        match size_change {
+            SizeChange::None => (),
+            SizeChange::SetTo { old, new } => {
+                self.set_capacity(context.dfg, old, new, |c| c);
+            }
+            SizeChange::Inc { old, new } => {
+                self.set_capacity(context.dfg, old, new, |c| {
+                    // Checked addition because increasing the capacity must increase it (cannot wrap around or saturate).
+                    c.checked_add(1).expect("Vector capacity overflow")
+                });
+            }
+            SizeChange::Dec { old, new } => {
+                // We use a saturating sub here as calling `pop_front` or `pop_back` on a zero-length vector
+                // would otherwise underflow.
+                self.set_capacity(context.dfg, old, new, |c| c.saturating_sub(1));
+            }
+            SizeChange::Many(changes) => {
+                for change in changes {
+                    self.change_size(change, context);
+                }
+            }
+        }
+    }
+
     /// Set the capacity of the new vector based on the capacity of the old array/vector.
     fn set_capacity(
         &mut self,
@@ -398,20 +406,20 @@ impl Context {
                     arguments.iter().map(|x| dfg.type_of_value(*x)).collect::<Vec<_>>();
                 let results_types =
                     results.iter().map(|x| dfg.type_of_value(*x)).collect::<Vec<_>>();
+
                 assert_eq!(arguments_types, results_types);
-                let old =
-                    *arguments.last().expect("expected at least one argument to Hint::BlackBox");
-                if self.vector_sizes.contains_key(&old) {
-                    if arguments.len() != 1 {
-                        assert!(arguments.len() == 2);
-                        assert!(matches!(arguments_types[0], Type::Numeric(_)));
+
+                let mut changes = Vec::new();
+                for (i, argument) in arguments.iter().enumerate() {
+                    if self.vector_sizes.contains_key(argument) {
+                        assert!(matches!(arguments_types[i - 1], Type::Numeric(_)));
+                        assert!(matches!(arguments_types[i], Type::Vector(_)));
+                        let new = results[i];
+                        changes.push(SizeChange::SetTo { old: *argument, new });
                     }
-                    assert!(matches!(arguments_types.last().unwrap(), Type::Vector(_)));
-                    let new = *results.last().unwrap();
-                    SizeChange::SetTo { old, new }
-                } else {
-                    SizeChange::None
                 }
+
+                SizeChange::Many(changes)
             }
 
             // These cases don't affect vector capacities
@@ -451,6 +459,7 @@ enum SizeChange {
         old: ValueId,
         new: ValueId,
     },
+    Many(Vec<SizeChange>),
 }
 
 #[cfg(debug_assertions)]
```

### test_programs/execution_success/regression_10975/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_10975"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_success/regression_10975/Prover.toml
```diff
@@ -0,0 +1,3 @@
+flag = true
+val = "abc"
+val2 = "a"
```

### test_programs/execution_success/regression_10975/src/main.nr
```diff
@@ -0,0 +1,38 @@
+fn main(val: str<3>, flag: bool, val2: str<1>) {
+    std::hint::black_box(());
+    example2(val, flag);
+    example3(val2);
+
+    // TODO(https://github.com/noir-lang/noir/issues/11134): Still broken
+    // example4(val, flag);
+}
+
+fn example2(val: str<3>, flag: bool) {
+    let b = val.as_bytes();
+    let s = b.as_vector();
+    let (_, s1) = s.pop_front();
+    let (s2, _) = s.pop_back();
+    let (s3, s4, _) = std::hint::black_box((s1, s2, 1));
+    let _ = if flag { s3 } else { s4 };
+}
+
+fn example3(val: str<1>) {
+    let b = val.as_bytes();
+    let s = b.as_vector();
+    let _ = std::hint::black_box((1, s));
+}
+
+// fn example4(val: str<3>, flag: bool) {
+//     let b = val.as_bytes();
+//     let s = b.as_vector();
+//     let (_, s1) = s.pop_front();
+//     let a = std::hint::black_box(|| {
+//         s1
+//     });
+//     let a = if flag {
+//         a()
+//     } else {
+//         &[123]
+//     };
+//     println(a);
+// }
```

### tooling/nargo_cli/tests/snapshots/execution_success/regression_10975/execute__tests__expanded.snap
```diff
@@ -0,0 +1,24 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main(val: str<3>, flag: bool, val2: str<1>) {
+    std::hint::black_box(());
+    example2(val, flag);
+    example3(val2);
+}
+
+fn example2(val: str<3>, flag: bool) {
+    let b: [u8; 3] = val.as_bytes();
+    let s: [u8] = b.as_vector();
+    let (_, s1): (u8, [u8]) = s.pop_front();
+    let (s2, _): ([u8], u8) = s.pop_back();
+    let (s3, s4, _): ([u8], [u8], Field) = std::hint::black_box((s1, s2, 1_Field));
+    let _: [u8] = if flag { s3 } else { s4 };
+}
+
+fn example3(val: str<1>) {
+    let b: [u8; 1] = val.as_bytes();
+    let s: [u8] = b.as_vector();
+    let _: (Field, [u8]) = std::hint::black_box((1_Field, s));
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/regression_10975/execute__tests__stdout.snap
```diff
@@ -0,0 +1,5 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stdout
+---
+
```
