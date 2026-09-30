# [?] fix(compiler): handle compiler panics as error

## Summary
Severity: Unknown
Chain: Starknet
Component: eqlabs/pathfinder
Published: 2023-11-28
Source: https://github.com/software-mansion/pathfinder/commit/f344465d0de2e5ae978d6c584a77018e74e8e460
Type: security-commit

## Details
fix(compiler): handle compiler panics as error

The Cairo compiler panics for certain input programs, possibly panicking
our JSON-RPC handler or sync tasks.

This commit catches compiler panics and simply converts those to
errors so that we can gracefully handle those errors (eg. fall back
to fetching the CASM definition from the gateway).

## Patch
### crates/compiler/src/lib.rs
```diff
@@ -21,15 +21,19 @@ pub fn compile_to_casm(
     const V_0_11_1: semver::Version = semver::Version::new(0, 11, 1);
     const V_0_11_2: semver::Version = semver::Version::new(0, 11, 2);
 
-    match version
-        .parse_as_semver()
-        .context("Deciding on compiler version")?
-    {
-        Some(v) if v > V_0_11_2 => v2::compile(definition),
-        Some(v) if v > V_0_11_1 => v1_1_1::compile(definition),
-        Some(v) if v > V_0_11_0 => v1_0_0_rc0::compile(definition),
-        _ => v1_0_0_alpha6::compile(definition),
-    }
+    let result = std::panic::catch_unwind(|| {
+        match version
+            .parse_as_semver()
+            .context("Deciding on compiler version")?
+        {
+            Some(v) if v > V_0_11_2 => v2::compile(definition),
+            Some(v) if v > V_0_11_1 => v1_1_1::compile(definition),
+            Some(v) if v > V_0_11_0 => v1_0_0_rc0::compile(definition),
+            _ => v1_0_0_alpha6::compile(definition),
+        }
+    });
+
+    result.unwrap_or_else(|e| Err(panic_error(e)))
 }
 
 /// Compile a Sierra class definition to CASM _with the latest compiler we support_.
@@ -40,7 +44,18 @@ pub fn compile_to_casm_with_latest_compiler(sierra_definition: &[u8]) -> anyhow:
     let definition = serde_json::from_slice::<FeederGatewayContractClass<'_>>(sierra_definition)
         .context("Parsing Sierra class")?;
 
-    v2::compile(definition)
+    let result = std::panic::catch_unwind(|| v2::compile(definition));
+    result.unwrap_or_else(|e| Err(panic_error(e)))
+}
+
+fn panic_error(e: Box<dyn std::any::Any>) -> anyhow::Error {
+    match e.downcast_ref::<&str>() {
+        Some(e) => anyhow::anyhow!("Compiler panicked: {}", e),
+        None => match e.downcast_ref::<String>() {
+            Some(e) => anyhow::anyhow!("Compiler panicked: {}", e),
+            None => anyhow::anyhow!("Compiler panicked"),
+        },
+    }
 }
 
 mod v1_0_0_alpha6 {
```
