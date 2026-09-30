# [?] fix: remove panic from `init_log_level` in `acvm_js` (#4195)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-01-29
Source: https://github.com/noir-lang/noir/commit/2e26530bf53006c1ed4fee310bcaa905c95dd95b
Type: security-commit

## Details
fix: remove panic from `init_log_level` in `acvm_js` (#4195)

# Description

## Problem\*

Resolves <!-- Link to GitHub Issue -->

## Summary\*

Looking at the [CI
logs](https://github.com/noir-lang/noir/actions/runs/7698147053/job/20976987617?pr=4194#step:6:16),
the ACVM JS failures seem to be happening inside the `init_log_lebel`
function. I'm not sure how this panic would be triggered intermittently
but this PR removes it in favour of returning a JS error as we shouldn't
assume that user inputted log levels are valid.


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
### acvm-repo/acvm_js/src/logging.rs
```diff
@@ -1,3 +1,4 @@
+use js_sys::{Error, JsString};
 use tracing_subscriber::prelude::*;
 use tracing_subscriber::EnvFilter;
 use tracing_web::MakeWebConsoleWriter;
@@ -7,12 +8,15 @@ use wasm_bindgen::prelude::*;
 ///
 /// @param {LogLevel} level - The maximum level of logging to be emitted.
 #[wasm_bindgen(js_name = initLogLevel, skip_jsdoc)]
-pub fn init_log_level(filter: String) {
+pub fn init_log_level(filter: String) -> Result<(), JsLogInitError> {
     // Set the static variable from Rust
     use std::sync::Once;
 
-    let filter: EnvFilter =
-        filter.parse().expect("Could not parse log filter while initializing logger");
+    let filter: EnvFilter = filter.parse().map_err(|err| {
+        JsLogInitError::constructor(
+            format!("Could not parse log filter while initializing logger: {err}").into(),
+        )
+    })?;
 
     static SET_HOOK: Once = Once::new();
     SET_HOOK.call_once(|| {
@@ -23,4 +27,19 @@ pub fn init_log_level(filter: String) {
 
         tracing_subscriber::registry().with(fmt_layer.with_filter(filter)).init();
     });
+
+    Ok(())
+}
+
+/// `LogInitError` is a raw js error.
+/// It'd be ideal that `LogInitError` was a subclass of Error, but for that we'd need to use JS snippets or a js module.
+/// Currently JS snippets don't work with a nodejs target. And a module would be too much for just a custom error type.
+#[wasm_bindgen]
+extern "C" {
+    #[wasm_bindgen(extends = Error, js_name = "LogInitError", typescript_type = "LogInitError")]
+    #[derive(Clone, Debug, PartialEq, Eq)]
+    pub type JsLogInitError;
+
+    #[wasm_bindgen(constructor, js_class = "Error")]
+    fn constructor(message: JsString) -> JsLogInitError;
 }
```
