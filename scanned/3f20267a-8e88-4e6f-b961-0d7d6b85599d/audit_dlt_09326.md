# [?] fix(debugger): don't panic when arena is empty (#6547)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2023-12-08
Source: https://github.com/foundry-rs/foundry/commit/fb601f535e563001210c142118c550b8422db335
Type: security-commit

## Details
fix(debugger): don't panic when arena is empty (#6547)

## Patch
### crates/debugger/src/tui/mod.rs
```diff
@@ -130,6 +130,8 @@ impl Debugger {
             .spawn(move || Self::event_listener(tx))
             .expect("failed to spawn thread");
 
+        eyre::ensure!(!cx.debug_arena().is_empty(), "debug arena is empty");
+
         // Draw the initial state.
         cx.draw(terminal)?;
 
```

### crates/forge/bin/cmd/test/mod.rs
```diff
@@ -188,7 +188,7 @@ impl TestArgs {
         // Prepare the test builder
         let should_debug = self.debug.is_some();
 
-        let mut runner_builder = MultiContractRunnerBuilder::default()
+        let runner_builder = MultiContractRunnerBuilder::default()
             .set_debug(should_debug)
             .initial_balance(evm_opts.initial_balance)
             .evm_spec(config.evm_spec_id())
@@ -197,7 +197,7 @@ impl TestArgs {
             .with_cheats_config(CheatsConfig::new(&config, evm_opts.clone()))
             .with_test_options(test_options.clone());
 
-        let mut runner = runner_builder.clone().build(
+        let runner = runner_builder.clone().build(
             project_root,
             output.clone(),
             env.clone(),
@@ -213,17 +213,6 @@ impl TestArgs {
                      Use --match-contract and --match-path to further limit the search."
                 );
             }
-            let test_funcs = runner.get_matching_test_functions(&filter);
-            // if we debug a fuzz test, we should not collect data on the first run
-            if !test_funcs.first().expect("matching function exists").inputs.is_empty() {
-                runner_builder = runner_builder.set_debug(false);
-                runner = runner_builder.clone().build(
-                    project_root,
-                    output.clone(),
-                    env.clone(),
-                    evm_opts.clone(),
-                )?;
-            }
         }
 
         let known_contracts = runner.known_contracts.clone();
@@ -307,7 +296,7 @@ impl TestArgs {
                     let source_contract = compact_to_contract(contract)?;
                     sources
                         .0
-                        .entry(id.clone().name)
+                        .entry(id.name.clone())
                         .or_default()
                         .insert(source.id, (source_code, source_contract));
                 }
```
