# [?] fix: return error rather instead of panicking on invalid circuit (#3976)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-01-08
Source: https://github.com/noir-lang/noir/commit/67201bfc21a9c8858aa86be9cd47d463fb78d925
Type: security-commit

## Details
fix: return error rather instead of panicking on invalid circuit (#3976)

# Description

## Problem\*

Resolves <!-- Link to GitHub Issue -->

## Summary\*

This PR replaces a panic on an invalid circuit in ACVM JS with an error.
If this occurs it's likely due to serialisation differences rather than
a user passing in garbage bytes so I've added that to the error message.

## Additional Context



## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[Exceptional Case]** Documentation to be submitted in a separate
PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### acvm-repo/acvm_js/src/execute.rs
```diff
@@ -61,8 +61,8 @@ pub async fn execute_circuit_with_black_box_solver(
     foreign_call_handler: ForeignCallHandler,
 ) -> Result<JsWitnessMap, Error> {
     console_error_panic_hook::set_once();
-    let circuit: Circuit =
-        Circuit::deserialize_circuit(&circuit).expect("Failed to deserialize circuit");
+    let circuit: Circuit = Circuit::deserialize_circuit(&circuit)
+        .map_err(|_| JsExecutionError::new("Failed to deserialize circuit. This is likely due to differing serialization formats between ACVM_JS and your compiler".to_string(), None))?;
 
     let mut acvm = ACVM::new(&solver.0, &circuit.opcodes, initial_witness.into());
 
```

### cspell.json
```diff
@@ -11,6 +11,7 @@
         "arity",
         "arkworks",
         "arraysort",
+        "barebones",
         "barretenberg",
         "bincode",
         "bindgen",
@@ -82,6 +83,7 @@
         "jmpif",
         "jmpifs",
         "jmps",
+        "jsdoc",
         "Jubjub",
         "keccak",
         "krate",
@@ -154,8 +156,7 @@
         "vecmap",
         "wasi",
         "Weierstraß",
-        "zshell",
-        "barebones"
+        "zshell"
     ],
     "ignorePaths": [
         "./**/node_modules/**"
```
