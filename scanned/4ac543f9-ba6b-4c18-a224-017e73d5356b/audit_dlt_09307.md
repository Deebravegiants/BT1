# [?] fix(`forge test --debug`): do not panic when user specifies both `--match-path` and `<PATH>` , bail instead (#10094)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-03-17
Source: https://github.com/foundry-rs/foundry/commit/f3be628d9453da53216f6603ed7b7471d5d21fe7
Type: security-commit

## Details
fix(`forge test --debug`): do not panic when user specifies both `--match-path` and `<PATH>` , bail instead (#10094)

cleanly exit instead of panic

## Patch
### crates/forge/bin/cmd/coverage.rs
```diff
@@ -274,7 +274,7 @@ impl CoverageArgs {
 
         let known_contracts = runner.known_contracts.clone();
 
-        let filter = self.test.filter(&config);
+        let filter = self.test.filter(&config)?;
         let outcome = self.test.run_tests(runner, config, verbosity, &filter, output).await?;
 
         outcome.ensure_ok(false)?;
```

### crates/forge/bin/cmd/test/mod.rs
```diff
@@ -2,7 +2,7 @@ use super::{install, test::filter::ProjectPathsAwareFilter, watch::WatchArgs};
 use alloy_primitives::U256;
 use chrono::Utc;
 use clap::{Parser, ValueHint};
-use eyre::{Context, OptionExt, Result};
+use eyre::{bail, Context, OptionExt, Result};
 use forge::{
     decode::decode_console_logs,
     gas_report::GasReport,
@@ -300,7 +300,7 @@ impl TestArgs {
         // Set up the project.
         let project = config.project()?;
 
-        let filter = self.filter(&config);
+        let filter = self.filter(&config)?;
         trace!(target: "forge::test", ?filter, "using filter");
 
         let sources_to_compile = self.get_sources_to_compile(&config, &filter)?;
@@ -815,19 +815,19 @@ impl TestArgs {
 
     /// Returns the flattened [`FilterArgs`] arguments merged with [`Config`].
     /// Loads and applies filter from file if only last test run failures performed.
-    pub fn filter(&self, config: &Config) -> ProjectPathsAwareFilter {
+    pub fn filter(&self, config: &Config) -> Result<ProjectPathsAwareFilter> {
         let mut filter = self.filter.clone();
         if self.rerun {
             filter.test_pattern = last_run_failures(config);
         }
         if filter.path_pattern.is_some() {
             if self.path.is_some() {
-                panic!("Can not supply both --match-path and |path|");
+                bail!("Can not supply both --match-path and |path|");
             }
         } else {
             filter.path_pattern = self.path.clone();
         }
-        filter.merge_with_config(config)
+        Ok(filter.merge_with_config(config))
     }
 
     /// Returns whether `BuildArgs` was configured with `--watch`
```

### crates/forge/bin/cmd/watch.rs
```diff
@@ -263,7 +263,7 @@ pub async fn watch_gas_snapshot(args: GasSnapshotArgs) -> Result<()> {
 /// test`
 pub async fn watch_test(args: TestArgs) -> Result<()> {
     let config: Config = args.build.load_config()?;
-    let filter = args.filter(&config);
+    let filter = args.filter(&config)?;
     // Marker to check whether to override the command.
     let no_reconfigure = filter.args().test_pattern.is_some() ||
         filter.args().path_pattern.is_some() ||
```
