# [?] fix(ssa interpreter): Add out of bounds error (#9147)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-07-08
Source: https://github.com/noir-lang/noir/commit/913ee6308f6ea040608df452a66bcb20bece3ca6
Type: security-commit

## Details
fix(ssa interpreter): Add out of bounds error (#9147)

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/errors.rs
```diff
@@ -68,6 +68,8 @@ pub enum InterpreterError {
     BlackBoxError { name: String, reason: String },
     #[error("Reached the unreachable")]
     ReachedTheUnreachable,
+    #[error("Array index {index} is out of bounds for array of length {length}")]
+    IndexOutOfBounds { index: u32, length: u32 },
 }
 
 /// These errors can only result from interpreting malformed SSA
```

### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -879,7 +879,11 @@ impl<'ssa, W: Write> Interpreter<'ssa, W> {
             let array = self.lookup_array_or_slice(array, "array get")?;
             let index = self.lookup_u32(index, "array get index")?;
             let index = index - offset.to_u32();
-            array.elements.borrow()[index as usize].clone()
+            let elements = array.elements.borrow();
+            let element = elements.get(index as usize).ok_or_else(|| {
+                InterpreterError::IndexOutOfBounds { index, length: elements.len() as u32 }
+            })?;
+            element.clone()
         } else {
             let typ = self.dfg().type_of_value(result);
             Value::uninitialized(&typ, result)
@@ -909,6 +913,11 @@ impl<'ssa, W: Write> Interpreter<'ssa, W> {
             let should_mutate =
                 if self.in_unconstrained_context() { *array.rc.borrow() == 1 } else { mutable };
 
+            let len = array.elements.borrow().len();
+            if index as usize >= len {
+                return Err(InterpreterError::IndexOutOfBounds { index, length: len as u32 });
+            }
+
             if should_mutate {
                 array.elements.borrow_mut()[index as usize] = value;
                 Value::ArrayOrSlice(array.clone())
```
