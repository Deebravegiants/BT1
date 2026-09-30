# [?] fix(cli): Do not panic on invalid arguments.

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkOS-test
Published: 2025-05-20
Source: https://github.com/AleoNet/snarkOS-test/commit/5696577f245f6c185df165b229756baff130007d
Type: security-commit

## Details
fix(cli): Do not panic on invalid arguments.

With this change the CLI also prints more context when there was an error.

## Patch
### cli/src/commands/start.rs
```diff
@@ -33,7 +33,7 @@ use snarkvm::{
 };
 
 use aleo_std::StorageMode;
-use anyhow::{Result, bail, ensure};
+use anyhow::{Context, Result, bail, ensure};
 use clap::Parser;
 use colored::Colorize;
 use core::str::FromStr;
@@ -190,45 +190,48 @@ impl Start {
             crate::helpers::initialize_logger(self.verbosity, self.nodisplay, self.logfile.clone(), shutdown.clone());
         // Initialize the runtime.
         Self::runtime().block_on(async move {
+            // Error messages.
+            let node_parse_error = || "Failed to parse node arguments";
+            let display_start_error = || "Failed to initialize the display";
+
             // Clone the configurations.
             let mut cli = self.clone();
             // Parse the network.
             match cli.network {
                 MainnetV0::ID => {
                     // Parse the node from the configurations.
-                    let node = cli.parse_node::<MainnetV0>(shutdown.clone()).await.expect("Failed to parse the node");
+                    let node = cli.parse_node::<MainnetV0>(shutdown.clone()).await.with_context(node_parse_error)?;
                     // If the display is enabled, render the display.
                     if !cli.nodisplay {
                         // Initialize the display.
-                        Display::start(node, log_receiver).expect("Failed to initialize the display");
+                        Display::start(node, log_receiver).with_context(display_start_error)?;
                     }
                 }
                 TestnetV0::ID => {
                     // Parse the node from the configurations.
-                    let node = cli.parse_node::<TestnetV0>(shutdown.clone()).await.expect("Failed to parse the node");
+                    let node = cli.parse_node::<TestnetV0>(shutdown.clone()).await.with_context(node_parse_error)?;
                     // If the display is enabled, render the display.
                     if !cli.nodisplay {
                         // Initialize the display.
-                        Display::start(node, log_receiver).expect("Failed to initialize the display");
+                        Display::start(node, log_receiver).with_context(display_start_error)?;
                     }
                 }
                 CanaryV0::ID => {
                     // Parse the node from the configurations.
-                    let node = cli.parse_node::<CanaryV0>(shutdown.clone()).await.expect("Failed to parse the node");
+                    let node = cli.parse_node::<CanaryV0>(shutdown.clone()).await.with_context(node_parse_error)?;
                     // If the display is enabled, render the display.
                     if !cli.nodisplay {
                         // Initialize the display.
-                        Display::start(node, log_receiver).expect("Failed to initialize the display");
+                        Display::start(node, log_receiver).with_context(display_start_error)?;
                     }
                 }
                 _ => panic!("Invalid network ID specified"),
             };
             // Note: Do not move this. The pending await must be here otherwise
             // other snarkOS commands will not exit.
             std::future::pending::<()>().await;
-        });
-
-        Ok(String::new())
+            Ok(String::new())
+        })
     }
 }
 
```

### snarkos/main.rs
```diff
@@ -72,7 +72,12 @@ fn main() -> anyhow::Result<()> {
     match cli.command.parse() {
         Ok(output) => println!("{output}\n"),
         Err(error) => {
-            println!("⚠️  {error}\n");
+            // Print the top level error and then any additional context.
+            println!("⚠️  {error}");
+            for entry in error.chain().skip(1) {
+                println!("     ↳ {entry}");
+            }
+            println!();
             exit(1);
         }
     }
```
