# [?] apollo_node_config: avoid panics in config load fn (#12318)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-02-05
Source: https://github.com/starkware-libs/sequencer/commit/4d356aba21ff8f582a284b072c0892676e13cfff
Type: security-commit

## Details
apollo_node_config: avoid panics in config load fn (#12318)

## Patch
### crates/apollo_node_config/src/config_utils.rs
```diff
@@ -220,14 +220,22 @@ pub fn load_and_validate_config(
     log_enabled: bool,
 ) -> Result<SequencerNodeConfig, ConfigError> {
     let config_load_result = SequencerNodeConfig::load_and_process(args);
-    let loaded_config =
-        config_load_result.unwrap_or_else(|err| panic!("Failed loading configuration: {err}"));
+    if let Err(error) = config_load_result {
+        error!("Failed loading configuration: {error}");
+        return Err(error);
+    }
+    let loaded_config = config_load_result.unwrap();
+
     if log_enabled {
         info!("Finished loading configuration.");
     }
-    if let Err(error) = loaded_config.validate_node_config() {
-        panic!("Config validation failed: {error}");
+
+    let config_validation_result = loaded_config.validate_node_config();
+    if let Err(error) = config_validation_result {
+        error!("Config validation failed: {error}");
+        return Err(error);
     }
+
     if log_enabled {
         info!("Finished validating configuration.");
         info!("Config map:");
```
