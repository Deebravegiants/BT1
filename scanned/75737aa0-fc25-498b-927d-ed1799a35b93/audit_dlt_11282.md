# [?] fix(ssa-interpreter): Ignore index overflow when side effects are disabled (#10183)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-10-14
Source: https://github.com/noir-lang/noir/commit/f8b6e72a31836f824f11a44d2ba8754af8d990a1
Type: security-commit

## Details
fix(ssa-interpreter): Ignore index overflow when side effects are disabled (#10183)

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -964,24 +964,39 @@ impl<'ssa, W: Write> Interpreter<'ssa, W> {
         result: ValueId,
         side_effects_enabled: bool,
     ) -> IResult<()> {
+        // When there is a problem indexing the array, but side effects are disabled,
+        // define the value as uninitialized.
+        let uninitialized = |this: &mut Self| {
+            let typ = this.dfg().type_of_value(result);
+            let value = Value::uninitialized(&typ, result);
+            this.define(result, value)
+        };
+
         let offset = self.dfg().array_offset(array, index);
         let array = self.lookup_array_or_slice(array, "array get")?;
         let length = array.elements.borrow().len() as u32;
-        let index = self.lookup_array_index(index, "array get index", length)?;
+
+        let index = match self.lookup_array_index(index, "array get index", length) {
+            Err(InterpreterError::IndexOutOfBounds { .. }) if !side_effects_enabled => {
+                return uninitialized(self);
+            }
+            other => other?,
+        };
         let mut index = index - offset.to_u32();
 
-        let element = if length == 0 {
+        if length == 0 {
             // Accessing an array of 0-len is replaced by asserting
             // the branch is not-taken during acir-gen and
             // a zeroed type is used in case of array get
             // So we can simply replace it with uninitialized value
             if side_effects_enabled {
                 return Err(InterpreterError::IndexOutOfBounds { index: index.into(), length });
             } else {
-                let typ = self.dfg().type_of_value(result);
-                Value::uninitialized(&typ, result)
+                return uninitialized(self);
             }
-        } else {
+        }
+
+        let element = {
             // An array_get with false side_effects_enabled is replaced
             // by a load at a valid index during acir-gen.
             if !side_effects_enabled {
```

### test_programs/execution_success/regression_10180/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_10180"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_success/regression_10180/Prover.toml
```diff
@@ -0,0 +1,2 @@
+b = true
+return = "193432430920915057603408161267722629873"
```

### test_programs/execution_success/regression_10180/src/main.nr
```diff
@@ -0,0 +1,12 @@
+global G_B: [(str<2>, Field)] = &[
+    ("SM", 193432430920915057603408161267722629873),
+    ("QK", 28517051330822917784420357897851281178),
+    ("XJ", -303354957477210748157621923488550325890),
+];
+fn main(b: bool) -> pub Field {
+    if b {
+        G_B[(1783103175_u32 % G_B.len())].1
+    } else {
+        (G_B[1771627614_u32].1 / G_B[2334904280_u32].1)
+    }
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/regression_10180/execute__tests__expanded.snap
```diff
@@ -0,0 +1,17 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+global G_B: [(str<2>, Field)] = &[
+    ("SM", 193432430920915057603408161267722629873),
+    ("QK", 28517051330822917784420357897851281178),
+    ("XJ", -303354957477210748157621923488550325890),
+];
+
+fn main(b: bool) -> pub Field {
+    if b {
+        G_B[1783103175_u32 % G_B.len()].1
+    } else {
+        G_B[1771627614_u32].1 / G_B[2334904280_u32].1
+    }
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/regression_10180/execute__tests__stdout.snap
```diff
@@ -0,0 +1,5 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stdout
+---
+[regression_10180] Circuit output: 0x9185bb28e2cfba7cb4079a5c3ada32f1
```
