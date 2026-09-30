# [?] fix: fix panic in forc-debug (#6165)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-06-21
Source: https://github.com/FuelLabs/sway/commit/c186d93155d0ef9f4432773be08c7da6d0fdf6de
Type: security-commit

## Details
fix: fix panic in forc-debug (#6165)

## Description

https://app.warp.dev/block/iedebqr2dgZIuM5N0ZNlkU



## Checklist

- [ ] I have linked to any relevant issues.
- [ ] I have commented my code, particularly in hard-to-understand
areas.
- [ ] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] If my change requires substantial documentation changes, I have
[requested support from the DevRel
team](https://github.com/FuelLabs/devrel-requests/issues/new/choose)
- [ ] I have added tests that prove my fix is effective or that my
feature works.
- [ ] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [ ] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [ ] I have requested a review from the relevant team or maintainers.

## Patch
### Cargo.lock
```diff
@@ -2059,6 +2059,7 @@ dependencies = [
  "escargot",
  "forc-pkg",
  "forc-test",
+ "forc-tracing 0.61.0",
  "fuel-core-client",
  "fuel-types",
  "fuel-vm",
```

### forc-plugins/forc-debug/Cargo.toml
```diff
@@ -14,6 +14,7 @@ clap = { version = "4.5.4", features = ["derive", "env"] }
 dap = "0.4.1-alpha1"
 forc-pkg = { version = "0.61.0", path = "../../forc-pkg" }
 forc-test = { version = "0.61.0", path = "../../forc-test" }
+forc-tracing = { version = "0.61.0", path = "../../forc-tracing" }
 fuel-core-client = { workspace = true }
 fuel-types = { workspace = true, features = ["serde"] }
 fuel-vm = { workspace = true, features = ["serde"] }
```

### forc-plugins/forc-debug/src/main.rs
```diff
@@ -4,6 +4,7 @@ use forc_debug::{
     server::DapServer,
     ContractId, FuelClient, RunResult, Transaction,
 };
+use forc_tracing::{init_tracing_subscriber, println_error};
 use fuel_vm::consts::{VM_MAX_RAM, VM_REGISTER_COUNT, WORD_SIZE};
 use shellfish::{async_fn, Command as ShCommand, Shell};
 use std::error::Error;
@@ -21,9 +22,17 @@ pub struct Opt {
 }
 
 #[tokio::main]
-async fn main() -> Result<(), Box<dyn std::error::Error>> {
+async fn main() {
+    init_tracing_subscriber(Default::default());
     let config = Opt::parse();
 
+    if let Err(err) = run(&config).await {
+        println_error(&format!("{}", err));
+        std::process::exit(1);
+    }
+}
+
+async fn run(config: &Opt) -> Result<(), Box<dyn std::error::Error>> {
     if config.serve {
         return DapServer::default().start();
     }
@@ -123,7 +132,7 @@ async fn cmd_start_tx(state: &mut State, mut args: Vec<String>) -> Result<(), Bo
     }
 
     let tx_json = std::fs::read(path_to_tx_json)?;
-    let tx: Transaction = serde_json::from_slice(&tx_json).unwrap();
+    let tx: Transaction = serde_json::from_slice(&tx_json)?;
     let status = state.client.start_tx(&state.session_id, &tx).await?;
     pretty_print_run_result(&status);
 
```
