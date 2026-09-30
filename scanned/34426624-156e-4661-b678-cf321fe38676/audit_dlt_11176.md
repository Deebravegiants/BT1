# [?] fix: avoid panics by propagating errors in outputs parsing and proof writing (#2191)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2025-09-19
Source: https://github.com/0xMiden/miden-vm/commit/ea26d4cb63cc8d274e9dfaec69e7dc491e18e5d8
Type: security-commit

## Details
fix: avoid panics by propagating errors in outputs parsing and proof writing (#2191)

## Patch
### miden-vm/src/cli/data.rs
```diff
@@ -97,7 +97,12 @@ impl OutputFile {
 
     /// Converts stack output vector to [StackOutputs].
     pub fn stack_outputs(&self) -> Result<StackOutputs, String> {
-        let stack = self.stack.iter().map(|v| v.parse::<u64>().unwrap()).collect::<Vec<u64>>();
+        let stack = self
+            .stack
+            .iter()
+            .map(|v| v.parse::<u64>())
+            .collect::<Result<Vec<u64>, _>>()
+            .map_err(|err| format!("Failed to parse stack output as u64 - {err}"))?;
 
         StackOutputs::try_from_ints(stack)
             .map_err(|e| format!("Construct stack outputs failed {e}"))
@@ -223,7 +228,8 @@ impl ProofFile {
         let proof_bytes = proof.to_bytes();
 
         // write proof bytes to file
-        file.write_all(&proof_bytes).unwrap();
+        file.write_all(&proof_bytes)
+            .map_err(|err| format!("Failed to write proof file `{}` - {}", path.display(), err))?;
 
         Ok(())
     }
```
