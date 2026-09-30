# [?] Merge pull request #1985 from opentensor/fix-rpc-panic-2

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2025-08-27
Source: https://github.com/RaoFoundation/subtensor/commit/a39a7a2beb52e5747b8b49cae02ad0fd9b3e419e
Type: security-commit

## Details
Merge pull request #1985 from opentensor/fix-rpc-panic-2

Fix node flag rpc panic

## Patch
### node/src/command.rs
```diff
@@ -318,14 +318,14 @@ fn customise_config(arg_matches: &ArgMatches, config: Configuration) -> Configur
 
     // If the operator did **not** supply `--rpc-max-subscriptions-per-connection` set to high value.
     config.rpc.max_subs_per_conn = match arg_matches
-        .value_source("rpc-max-subscriptions-per-connection")
+        .value_source("rpc_max_subscriptions_per_connection")
     {
         Some(ValueSource::CommandLine) => cli.run.rpc_params.rpc_max_subscriptions_per_connection,
         _ => 10000,
     };
 
     // If the operator did **not** supply `--rpc-max-connections` set to high value.
-    config.rpc.max_connections = match arg_matches.value_source("rpc-max-connections") {
+    config.rpc.max_connections = match arg_matches.value_source("rpc_max_connections") {
         Some(ValueSource::CommandLine) => cli.run.rpc_params.rpc_max_connections,
         _ => 10000,
     };
```
