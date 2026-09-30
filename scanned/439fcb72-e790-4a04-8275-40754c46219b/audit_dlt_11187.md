# [?] fix: resolve u32split stack underflow for single-element stack

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2022-01-23
Source: https://github.com/0xMiden/miden-vm/commit/a3796ad3c75911444168b42044205bf550bee161
Type: security-commit

## Details
fix: resolve u32split stack underflow for single-element stack

## Patch
### processor/src/operations/u32_ops.rs
```diff
@@ -15,9 +15,10 @@ impl Process {
         let a = self.stack.get(0);
         let (lo, hi) = split_element(a);
 
+        // shift right first so stack depth is increased before we attempt to set the output values
+        self.stack.shift_right(1);
         self.stack.set(0, hi);
         self.stack.set(1, lo);
-        self.stack.shift_right(1);
         Ok(())
     }
 
```
