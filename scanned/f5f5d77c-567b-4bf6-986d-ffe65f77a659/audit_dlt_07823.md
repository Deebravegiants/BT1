# [?] Fix panic on startup in debug build (#5917)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2024-06-13
Source: https://github.com/sigp/lighthouse/commit/5789db042d9d5da88db3b5303fd3f3da75ec1573
Type: security-commit

## Details
Fix panic on startup in debug build (#5917)

* Fix panic in debug build

* make cli-local to update the book

## Patch
### account_manager/src/lib.rs
```diff
@@ -18,7 +18,7 @@ pub const WALLETS_DIR_FLAG: &str = "wallets-dir";
 
 pub fn cli_app() -> Command {
     Command::new(CMD)
-        .visible_aliases(["a", "am", "account", CMD])
+        .visible_aliases(["a", "am", "account"])
         .about("Utilities for generating and managing Ethereum 2.0 accounts.")
         .display_order(0)
         .arg(
```

### book/src/help_general.md
```diff
@@ -9,7 +9,7 @@ Usage: lighthouse [OPTIONS] [COMMAND]
 Commands:
   account_manager
           Utilities for generating and managing Ethereum 2.0 accounts. [aliases:
-          a, am, account, account_manager]
+          a, am, account]
   beacon_node
           The primary component which connects to the Ethereum 2.0 P2P network
           and downloads, verifies and stores blocks. Provides a HTTP API for
@@ -30,7 +30,7 @@ Commands:
           validator]
   validator_manager
           Utilities for managing a Lighthouse validator client via the HTTP API.
-          [aliases: vm, validator-manager, validator_manager]
+          [aliases: vm, validator-manager]
   help
           Print this message or the help of the given subcommand(s)
 
```

### validator_manager/src/lib.rs
```diff
@@ -40,7 +40,7 @@ impl DumpConfig {
 
 pub fn cli_app() -> Command {
     Command::new(CMD)
-        .visible_aliases(["vm", "validator-manager", CMD])
+        .visible_aliases(["vm", "validator-manager"])
         .display_order(0)
         .styles(get_color_style())
         .about("Utilities for managing a Lighthouse validator client via the HTTP API.")
```
