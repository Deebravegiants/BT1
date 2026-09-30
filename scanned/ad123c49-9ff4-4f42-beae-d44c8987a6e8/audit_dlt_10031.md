# [?] Merge remote-tracking branch 'origin/prevelidate_tx' into l-monninger/fix-sequence-number-panic

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-07-15
Source: https://github.com/movement-network/movement/commit/13ef43dd2822385d57f37c80b4a87a39eaace858
Type: security-commit

## Details
Merge remote-tracking branch 'origin/prevelidate_tx' into l-monninger/fix-sequence-number-panic

## Patch
### Cargo.toml
```diff
@@ -22,6 +22,9 @@ members = [
     "networks/suzuka/*",
     "protocol-units/settlement/mcr/setup",
     "protocol-units/settlement/mcr/anvil",
+    "protocol-units/bridge/shared",
+    "protocol-units/bridge/cli",
+    "protocol-units/bridge/service",
 ]
 
 [workspace.package]
@@ -90,35 +93,36 @@ serde_yaml = "0.9.34"
 ## Aptos dependencies
 ### We use a forked version so that we can override dependency versions. This is required
 ### to be avoid dependency conflicts with other Sovereign Labs crates.
-aptos-api = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-api-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-bitvec = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-block-executor = { git = "https://github.com/movementlabsxyz/aptos-core.git", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-cached-packages = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-config = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-consensus-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-crypto = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8", features = [
+aptos-api = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-api-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-bitvec = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-block-executor = { git = "https://github.com/movementlabsxyz/aptos-core.git", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-cached-packages = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-config = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-consensus-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-crypto = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c", features = [
     "cloneable-private-keys",
 ] }
-aptos-db = { git = "https://github.com/movementlabsxyz/aptos-core.git", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-executor = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-executor-test-helpers = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-executor-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-faucet-core = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-framework = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-language-e2e-tests = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-mempool = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-proptest-helpers = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-sdk = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-state-view = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-storage-interface = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-temppath = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-vm = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-vm-genesis = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-vm-logging = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-logger = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
-aptos-vm-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "d41e9c0c35ce563a3f3b070656abddeb994988e8" }
+aptos-db = { git = "https://github.com/movementlabsxyz/aptos-core.git", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-executor = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-executor-test-helpers = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-executor-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-faucet-core = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-framework = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-language-e2e-tests = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-mempool = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-proptest-helpers = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-sdk = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-state-view = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-storage-interface = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-temppath = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-vm = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-vm-genesis = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-vm-logging = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-vm-validator = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-logger = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
+aptos-vm-types = { git = "https://github.com/movementlabsxyz/aptos-core", rev = "b54d443967ff4ce621a84f7c09f9a59a0b03e01c" }
 bcs = { git = "https://github.com/aptos-labs/bcs.git", rev = "d31fab9d81748e2594be5cd5cdf845786a30562d" }
 ethereum-types = "0.14.1"
 ethers = "=2.0.10"
@@ -159,8 +163,8 @@ alloy = { git = "https://github.com/alloy-rs/alloy.git", package = "alloy", rev
     "signers",
     "signer-yubihsm",
     "pubsub",
-    "providers"
-]}
+    "providers",
+] }
 alloy-contract = { git = "https://github.com/alloy-rs/alloy.git", rev = "83343b172585fe4e040fb104b4d1421f58cbf9a2" }
 alloy-network = { git = "https://github.com/alloy-rs/alloy.git", rev = "83343b172585fe4e040fb104b4d1421f58cbf9a2" }
 alloy-primitives = { version = "0.7.2", default-features = false }
@@ -219,7 +223,7 @@ rayon = "1.10.0"
 reqwest = "0.12.4"
 risc0-build = "0.20"
 risc0-zkvm = { version = "0.21", features = ["std", "getrandom"] }
-rocksdb = { version = "0.21.0", features = [
+rocksdb = { version = "0.22.0", features = [
     "snappy",
     "lz4",
     "zstd",
@@ -248,7 +252,7 @@ url = "2.2.2"
 x25519-dalek = "1.0.1"
 zstd-sys = "2.0.9"
 inotify = "0.10.2"
-rustix = "0.38.34" 
+rustix = "0.38.34"
 
 
 [workspace.lints.rust]
@@ -273,6 +277,4 @@ opt-level = 3
 [patch.crates-io]
 merlin = { git = "https://github.com/aptos-labs/merlin" }
 x25519-dalek = { git = "https://github.com/aptos-labs/x25519-dalek", branch = "zeroize_v1" }
-sha2 = { git = "https://github.com/risc0/RustCrypto-hashes", tag = "sha2-v0.10.8-risczero.0" }
-ed25519-dalek = { git = "https://github.com/risc0/curve25519-dalek", tag = "curve25519-4.1.0-risczero.1" }
 zstd-sys = { git = "https://github.com/gyscos/zstd-rs.git", rev = "1779b385b42b08f958b767a37878dfa6a0b4f6a4" }
```

### README.md
```diff
@@ -34,7 +34,7 @@ classical semantic versioning.
 ## Prerequisites
 ### Prerequisites - Just command
 `just` is a handy way to save and run project-specific commands. Please install it
-[following just install instructioins](https://github.com/casey/just?tab=readme-ov-file#installation). `macOS` and `debian` based systems instructions below.
+[following just install instructions](https://github.com/casey/just?tab=readme-ov-file#installation). `macOS` and `debian` based systems instructions below.
 
 ### Just command - macOS
 ```bash 
```

### docs/movement-node/run/manual/README.md
```diff
@@ -6,7 +6,7 @@ We recommend that you run a movement node using containers to leverage the porta
 1. Ubuntu 22.04 amd64
 2. [Docker](https://docs.docker.com/engine/install/ubuntu/)
 3. [Docker compose](https://docs.docker.com/compose/install/linux/)
-4. Make sure you are logged in as the user that wants to run the node
+4. Make sure you are logged in as the user who wants to run the node
 
 ## Run the movement node as an RPC provider
 
@@ -119,4 +119,4 @@ sudo systemctl status suzuka-full-node.service
 9. Have a look at the logs. Display full logs line by using the follow flag `-f`
 ```bash
 sudo journalctl -u suzuka-full-node.service -f
-```
\ No newline at end of file
+```
```

### flake.lock
```diff
@@ -53,24 +53,6 @@
         "type": "github"
       }
     },
-    "flake-utils_3": {
-      "inputs": {
-        "systems": "systems_2"
-      },
-      "locked": {
-        "lastModified": 1705309234,
-        "narHash": "sha256-uNRRNRKmJyCRC/8y1RqBkqWBLM034y4qN7EprSdmgyA=",
-        "owner": "numtide",
-        "repo": "flake-utils",
-        "rev": "1ef2e671c3b0c19053962c07dbda38332dcebf26",
-        "type": "github"
-      },
-      "original": {
-        "owner": "numtide",
-        "repo": "flake-utils",
-        "type": "github"
-      }
-    },
     "foundry": {
       "inputs": {
         "flake-utils": "flake-utils_2",
@@ -107,17 +89,17 @@
     },
     "nixpkgs_2": {
       "locked": {
-        "lastModified": 1715266358,
-        "narHash": "sha256-doPgfj+7FFe9rfzWo1siAV2mVCasW+Bh8I1cToAXEE4=",
+        "lastModified": 1719908484,
+        "narHash": "sha256-ol3YPu/4U4tOLsEG1NOo+ICON4BnKF16zB6AfbZE9xA=",
         "owner": "NixOS",
         "repo": "nixpkgs",
-        "rev": "f1010e0469db743d14519a1efd37e23f8513d714",
+        "rev": "ae0b2bf3fab958fc7d83a7893ee57175fd2609d3",
         "type": "github"
       },
       "original": {
         "owner": "NixOS",
         "repo": "nixpkgs",
-        "rev": "f1010e0469db743d14519a1efd37e23f8513d714",
+        "rev": "ae0b2bf3fab958fc7d83a7893ee57175fd2609d3",
         "type": "github"
       }
     },
@@ -148,20 +130,20 @@
     },
     "rust-overlay": {
       "inputs": {
-        "flake-utils": "flake-utils_3",
         "nixpkgs": "nixpkgs_3"
       },
       "locked": {
-        "lastModified": 1712024007,
-        "narHash": "sha256-52cf+mHZJbSaDFdsBj6vN1hH52AXsMgEpS/ajzc9yQE=",
+        "lastModified": 1719886738,
+        "narHash": "sha256-6eaaoJUkr4g9J/rMC4jhj3Gv8Sa62rvlpjFe3xZaSjM=",
         "owner": "oxalica",
         "repo": "rust-overlay",
-        "rev": "d45d957dc3c48792af7ce58eec5d84407655e8fa",
+        "rev": "db12d0c6ef002f16998723b5dd619fa7b8997086",
         "type": "github"
       },
       "original": {
         "owner": "oxalica",
         "repo": "rust-overlay",
+        "rev": "db12d0c6ef002f16998723b5dd619fa7b8997086",
         "type": "github"
       }
     },
@@ -179,21 +161,6 @@
         "repo": "default",
         "type": "github"
       }
-    },
-    "systems_2": {
-      "locked": {
-        "lastModified": 1681028828,
-        "narHash": "sha256-Vy1rq5AaRuLzOxct8nz4T6wlgyUR7zLU309k9mBC768=",
-        "owner": "nix-systems",
-        "repo": "default",
-        "rev": "da67096a3b9bf56a91d16901293e51ba5b49a27e",
-        "type": "github"
-      },
-      "original": {
-        "owner": "nix-systems",
-        "repo": "default",
-        "type": "github"
-      }
     }
   },
   "root": "root",
```

### flake.nix
```diff
@@ -1,7 +1,7 @@
 {
   inputs = {
-    nixpkgs.url = "github:NixOS/nixpkgs/f1010e0469db743d14519a1efd37e23f8513d714";
-    rust-overlay.url = "github:oxalica/rust-overlay";
+    nixpkgs.url = "github:NixOS/nixpkgs/ae0b2bf3fab958fc7d83a7893ee57175fd2609d3";
+    rust-overlay.url = "github:oxalica/rust-overlay/db12d0c6ef002f16998723b5dd619fa7b8997086";
     flake-utils.url = "github:numtide/flake-utils";
     foundry.url = "github:shazow/foundry.nix/monthly"; 
     crane.url = "github:ipetkov/crane";
```

### networks/README.md
```diff
@@ -2,4 +2,4 @@
 This directory contains network runner entry points for the Movement Network. These are the entry points for running the Movement Network.
 
 ## `suzuka`
-Suzuka is the second network released in this repository after Monza which has since be removed whilst it was not being maintained. Suzuka features M1 data availability, Movement Aptos (Maptos) execution, and ETH settlement.
\ No newline at end of file
+Suzuka is the second network released in this repository after Monza which has since been removed whilst it was not being maintained. Suzuka features M1 data availability, Movement Aptos (Maptos) execution, and ETH settlement.
```

### networks/suzuka/suzuka-full-node/src/partial.rs
```diff
@@ -22,7 +22,7 @@ use tokio::sync::RwLock;
 use tokio_stream::StreamExt;
 use tracing::{debug, info, error};
 
-use std::future::{self, Future};
+use std::future::Future;
 use std::sync::Arc;
 use std::time::Duration;
 pub struct SuzukaPartialNode<T> {
@@ -250,7 +250,7 @@ where
 		}
 	}
 
-	Ok(future::pending().await)
+	Ok(())
 }
 
 impl<T> SuzukaFullNode for SuzukaPartialNode<T>
```

### protocol-units/bridge/cli/Cargo.toml
```diff
@@ -0,0 +1,17 @@
+[package]
+name = "bridge-cli"
+version.workspace = true
+edition.workspace = true
+license.workspace = true
+authors.workspace = true
+repository.workspace = true
+homepage.workspace = true
+publish.workspace = true
+rust-version.workspace = true
+
+# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html
+
+[dependencies]
+
+[lints]
+workspace = true
```

### protocol-units/bridge/cli/src/main.rs
```diff
@@ -0,0 +1,3 @@
+fn main() {
+	println!("Hello, world!");
+}
```

### protocol-units/bridge/contracts/lib/openzeppelin-contracts
```diff
@@ -1 +1 @@
-Subproject commit 4032b42694ff6599b17ffde65b2b64d7fc8a38f8
+Subproject commit dbb6104ce834628e473d2173bbc9d47f81a9eec3
```
