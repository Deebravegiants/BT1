# [?] fix: internal assembler error on local word overflow (#1844)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2025-06-05
Source: https://github.com/0xMiden/miden-vm/commit/d69f37d1d3f0f59c0cbd76b4735d66c19a26a7ba
Type: security-commit

## Details
fix: internal assembler error on local word overflow (#1844)

Given the following Miden assembly procedure:

proc.foo.1
    loc_storew.0
end

Compilation of this procedure would previously cause the assembler to
panic when calculating the maximum number of allowed locals. This commit
fixes this panic and turns it into an assembler error.

## Patch
### assembly/src/assembler/instruction/mem_ops.rs
```diff
@@ -138,7 +138,10 @@ pub fn local_to_absolute_addr(
     let max = if is_single {
         num_proc_locals - 1
     } else {
-        num_proc_locals - 4
+        // If a word local value is used, then the procedure needs at least 4 local values.
+        u16::checked_sub(num_proc_locals, 4).ok_or_else(|| AssemblyError::Other(Report::msg(
+            "number of procedure locals was set to less 4, but word-sized local values were used".to_string()
+        ).into()))?
     };
 
     // Local values are placed under the frame pointer, so we need to calculate the offset of the
```
