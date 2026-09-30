# [?] fix(prover): tokio thread stack overflow (#1604)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2025-02-28
Source: https://github.com/scroll-tech/scroll/commit/a5e2d71ebdc76a78ab2005468849db52543287de
Type: security-commit

## Details
fix(prover): tokio thread stack overflow (#1604)

## Patch
### prover/config.json
```diff
@@ -18,12 +18,12 @@
     "db_path": "unique-db-path-for-prover-1"
   },
   "low_version_circuit": {
-    "hard_fork_name": "Darvin",
+    "hard_fork_name": "darwin",
     "params_path": "params",
     "assets_path": "assets"
   },
   "high_version_circuit": {
-    "hard_fork_name": "DarvinV2",
+    "hard_fork_name": "darwinV2",
     "params_path": "params",
     "assets_path": "assets"
   }
```

### prover/src/main.rs
```diff
@@ -13,6 +13,7 @@ use scroll_proving_sdk::{
     prover::ProverBuilder,
     utils::{get_version, init_tracing},
 };
+use tokio::runtime;
 use utils::get_prover_type;
 
 #[derive(Parser, Debug)]
@@ -31,38 +32,45 @@ struct Args {
     log_file: Option<String>,
 }
 
-#[tokio::main]
-async fn main() -> anyhow::Result<()> {
-    init_tracing();
+fn main() -> anyhow::Result<()> {
+    let rt = runtime::Builder::new_multi_thread()
+        .thread_stack_size(16 * 1024 * 1024) // Set stack size to 16MB
+        .enable_all()
+        .build()
+        .expect("Failed to create Tokio runtime");
+
+    rt.block_on(async {
+        init_tracing();
 
-    let args = Args::parse();
+        let args = Args::parse();
 
-    if args.version {
-        println!("version is {}", get_version());
-        std::process::exit(0);
-    }
+        if args.version {
+            println!("version is {}", get_version());
+            std::process::exit(0);
+        }
 
-    let cfg = LocalProverConfig::from_file(args.config_file)?;
-    let sdk_config = cfg.sdk_config.clone();
-    let mut prover_types = vec![];
-    sdk_config
-        .prover
-        .circuit_types
-        .iter()
-        .for_each(|circuit_type| {
-            if let Some(pt) = get_prover_type(*circuit_type) {
-                if !prover_types.contains(&pt) {
-                    prover_types.push(pt);
+        let cfg = LocalProverConfig::from_file(args.config_file)?;
+        let sdk_config = cfg.sdk_config.clone();
+        let mut prover_types = vec![];
+        sdk_config
+            .prover
+            .circuit_types
+            .iter()
+            .for_each(|circuit_type| {
+                if let Some(pt) = get_prover_type(*circuit_type) {
+                    if !prover_types.contains(&pt) {
+                        prover_types.push(pt);
+                    }
                 }
-            }
-        });
-    let local_prover = LocalProver::new(cfg, prover_types);
-    let prover = ProverBuilder::new(sdk_config)
-        .with_proving_service(Box::new(local_prover))
-        .build()
-        .await?;
+            });
+        let local_prover = LocalProver::new(cfg, prover_types);
+        let prover = ProverBuilder::new(sdk_config)
+            .with_proving_service(Box::new(local_prover))
+            .build()
+            .await?;
 
-    prover.run().await;
+        prover.run().await;
 
-    Ok(())
+        Ok(())
+    })
 }
```
