# [?] fix(forc-pkg): Resolve runtime panic in registry dependency fetching (#7246)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2025-06-23
Source: https://github.com/FuelLabs/sway/commit/b21e87e4aa0ea6a7ebf1ff24b5f0474ff71e42b7
Type: security-commit

## Details
fix(forc-pkg): Resolve runtime panic in registry dependency fetching (#7246)

## Description
Fixes the "cannot start a runtime from within a runtime" panic when
fetching registry dependencies.

The synchronous fetch operation now safely blocks on the async IPFS
client by spawning a new OS thread when already inside a `tokio` runtime
context. Enabled the `with-send-sync` feature for
`ipfs-api-backend-hyper` to make its futures thread-safe.

## Checklist

- [ ] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
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
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

## Patch
### forc-pkg/Cargo.toml
```diff
@@ -21,7 +21,7 @@ futures.workspace = true
 git2 = { workspace = true, features = ["vendored-libgit2", "vendored-openssl"] }
 gix-url = { workspace = true, features = ["serde"] }
 hex.workspace = true
-ipfs-api-backend-hyper = { workspace = true, features = ["with-builder"] }
+ipfs-api-backend-hyper = { workspace = true, features = ["with-builder", "with-send-sync"] }
 petgraph = { workspace = true, features = ["serde-1"] }
 reqwest.workspace = true
 scopeguard.workspace = true
```

### forc-pkg/src/source/ipfs.rs
```diff
@@ -78,11 +78,13 @@ impl source::Fetch for Pinned {
                     "Fetching",
                     &format!("{} {}", ansiterm::Style::new().bold().paint(ctx.name), self),
                 );
-                let cid = &self.0;
+                let cid = self.0.clone();
+                let ipfs_node = ctx.ipfs_node().clone();
                 let ipfs_client = ipfs_client();
                 let dest = cache_dir();
-                crate::source::reg::block_on_any_runtime(async {
-                    match ctx.ipfs_node() {
+
+                crate::source::reg::block_on_any_runtime(async move {
+                    match ipfs_node {
                         source::IPFSNode::Local => {
                             println_action_green("Fetching", "with local IPFS node");
                             cid.fetch_with_client(&ipfs_client, &dest).await
@@ -95,7 +97,7 @@ impl source::Fetch for Pinned {
                                     ipfs_node_gateway_url
                                 ),
                             );
-                            cid.fetch_with_gateway_url(ipfs_node_gateway_url, &dest)
+                            cid.fetch_with_gateway_url(&ipfs_node_gateway_url, &dest)
                                 .await
                         }
                     }
```

### forc-pkg/src/source/reg/mod.rs
```diff
@@ -19,6 +19,7 @@ use std::{
     fs,
     path::{Path, PathBuf},
     str::FromStr,
+    thread,
     time::Duration,
 };
 
@@ -315,19 +316,26 @@ fn tmp_registry_package_dir(
 impl source::Pin for Source {
     type Pinned = Pinned;
     fn pin(&self, ctx: source::PinCtx) -> anyhow::Result<(Self::Pinned, PathBuf)> {
-        let pkg_name = ctx.name;
-        let cid = block_on_any_runtime(async {
-            with_tmp_fetch_index(ctx.fetch_id(), pkg_name, self, |index_file| async move {
-                let version = &self.version;
-                let pkg_entry = index_file
-                    .get(version)
-                    .ok_or_else(|| anyhow!("No {} found for {}", version, pkg_name))?;
-                let cid = Cid::from_str(pkg_entry.source_cid());
-                Ok(cid)
+        let pkg_name = ctx.name.to_string();
+        let fetch_id = ctx.fetch_id();
+        let source = self.clone();
+        let pkg_name = pkg_name.clone();
+
+        let cid = block_on_any_runtime(async move {
+            with_tmp_fetch_index(fetch_id, &pkg_name, &source, |index_file| {
+                let version = source.version.clone();
+                let pkg_name = pkg_name.clone();
+                async move {
+                    let pkg_entry = index_file
+                        .get(&version)
+                        .ok_or_else(|| anyhow!("No {} found for {}", version, pkg_name))?;
+                    Cid::from_str(pkg_entry.source_cid()).map_err(anyhow::Error::from)
+                }
             })
             .await
-        })??;
-        let path = registry_package_dir(&self.namespace, pkg_name, &self.version);
+        })?;
+
+        let path = registry_package_dir(&self.namespace, ctx.name, &self.version);
         let pinned = Pinned {
             source: self.clone(),
             cid,
@@ -357,15 +365,19 @@ impl source::Fetch for Pinned {
                         self.source.version
                     ),
                 );
-                block_on_any_runtime(async {
+                let pinned = self.clone();
+                let fetch_id = ctx.fetch_id();
+                let ipfs_node = ctx.ipfs_node().clone();
+
+                block_on_any_runtime(async move {
                     // If the user is trying to use public IPFS node with
                     // registry sources. Use fuel operated ipfs node
                     // instead.
-                    let node = match ctx.ipfs_node() {
-                        node if node == &IPFSNode::public() => &IPFSNode::fuel(),
+                    let node = match ipfs_node {
+                        node if node == IPFSNode::public() => IPFSNode::fuel(),
                         node => node,
                     };
-                    fetch(ctx.fetch_id(), self, node).await
+                    fetch(fetch_id, &pinned, &node).await
                 })?;
             }
         }
@@ -526,15 +538,29 @@ where
     Ok(res)
 }
 
-/// Execute an async block on the current Tokio runtime if available.
-/// If not in a runtime context, a new one is created to run the future.
+/// Execute an async block on a Tokio runtime.
+///
+/// If we are already in a runtime, this will spawn a new OS thread to create a new runtime.
+///
+/// If we are not in a runtime, a new runtime is created and the future is blocked on.
 pub(crate) fn block_on_any_runtime<F>(future: F) -> F::Output
 where
-    F: std::future::Future,
+    F: std::future::Future + Send + 'static,
+    F::Output: Send + 'static,
 {
-    if let Ok(handle) = tokio::runtime::Handle::try_current() {
-        handle.block_on(future)
+    if tokio::runtime::Handle::try_current().is_ok() {
+        // In a runtime context. Spawn a new thread to run the async code.
+        thread::spawn(move || {
+            let rt = tokio::runtime::Builder::new_current_thread()
+                .enable_all()
+                .build()
+                .unwrap();
+            rt.block_on(future)
+        })
+        .join()
+        .unwrap()
     } else {
+        // Not in a runtime context. Okay to create a new runtime and block.
         let rt = tokio::runtime::Builder::new_current_thread()
             .enable_all()
             .build()
```
