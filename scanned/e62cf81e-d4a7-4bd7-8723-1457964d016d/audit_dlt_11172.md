# [?] fix(cli): return error instead of panic on invalid --security value (#2689)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-02-14
Source: https://github.com/0xMiden/miden-vm/commit/0d6a0354f863421da0fe2688fabb98bc685757e3
Type: security-commit

## Details
fix(cli): return error instead of panic on invalid --security value (#2689)

## Patch
### miden-vm/src/cli/prove.rs
```diff
@@ -81,13 +81,15 @@ impl ProveCmd {
 
         let hash_fn = HashFunction::try_from(self.hasher.as_str())
             .map_err(|err| Report::msg(format!("{err}")))?;
-        Ok(match self.security.as_str() {
+        let proving_options = match self.security.as_str() {
             "96bits" => ProvingOptions::with_96_bit_security(hash_fn),
-            other => panic!(
-                "{other} is not a valid security setting. Currently only '96bits' is supported."
-            ),
-        }
-        .with_execution_options(exec_options))
+            other => {
+                return Err(Report::msg(format!(
+                    "{other} is not a valid security setting. Currently only '96bits' is supported."
+                )));
+            },
+        };
+        Ok(proving_options.with_execution_options(exec_options))
     }
     pub fn execute(&self) -> Result<(), Report> {
         println!("===============================================================================");
```
