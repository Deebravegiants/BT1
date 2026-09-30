# [?] Merge pull request from GHSA-xqqc-c5gw-c5r5

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/tendermint-rs
Published: 2022-12-14
Source: https://github.com/cometbft/tendermint-rs/commit/5c32f31b97ac3172775699fe0d4ba6003ca4fb18
Type: security-commit

## Details
Merge pull request from GHSA-xqqc-c5gw-c5r5

* Add the is_matching_chain_id() predicate

* Add TrustedBlockState::chain_id field

* Implement matching chain-id check in verifier

* Add test

* Add test for verifier

* Bump light client verifier and dependent crates to v0.28.0-pre.1

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Bump kvstore test light client dependency

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Bump version to v0.28.0

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Add changelog entries for security fix

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Prepare v0.28.0 release changelog

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Rebuild changelog

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Update release date in changelog

Signed-off-by: Thane Thomson <connect@thanethomson.com>

Signed-off-by: Thane Thomson <connect@thanethomson.com>
Co-authored-by: Thane Thomson <connect@thanethomson.com>

## Patch
### .changelog/v0.28.0/breaking/1249-light-client-verification-preds.md
```diff
@@ -0,0 +1,3 @@
+- `[tendermint-light-client-verifier]` Add `is_matching_chain_id`
+  method to the `VerificationPredicates` trait
+  ([#1249](https://github.com/informalsystems/tendermint-rs/pull/1249))
```

### .changelog/v0.28.0/breaking/1249-light-client-verifier.md
```diff
@@ -0,0 +1,3 @@
+- `[tendermint-light-client-verifier]` Add a
+  `chain_id` field to the `TrustedBlockState` struct
+  ([#1249](https://github.com/informalsystems/tendermint-rs/pull/1249))
```

### .changelog/v0.28.0/security/1249-light-client-security.md
```diff
@@ -0,0 +1,3 @@
+- `[tendermint-light-client]` Fix an issue where the light client was not
+  checking that the chain ID of the trusted and untrusted headers match
+  ([#1249](https://github.com/informalsystems/tendermint-rs/pull/1249))
```

### .changelog/v0.28.0/summary.md
```diff
@@ -0,0 +1,7 @@
+*Dec 13, 2022*
+
+This is primarily a security-related release, and although it's a breaking
+release, the breaking changes are relatively minor.
+
+It is highly recommended that all tendermint-rs light client users upgrade to
+this version immediately.
```

### CHANGELOG.md
```diff
@@ -1,5 +1,35 @@
 # CHANGELOG
 
+## v0.28.0
+
+*Dec 13, 2022*
+
+This is primarily a security-related release, and although it's a breaking
+release, the breaking changes are relatively minor.
+
+It is highly recommended that all tendermint-rs light client users upgrade to
+this version immediately.
+
+### BREAKING
+
+- `[tendermint-light-client-verifier]` Add a
+  `chain_id` field to the `TrustedBlockState` struct
+  ([#1249](https://github.com/informalsystems/tendermint-rs/pull/1249))
+- `[tendermint-light-client-verifier]` Add `is_matching_chain_id`
+  method to the `VerificationPredicates` trait
+  ([#1249](https://github.com/informalsystems/tendermint-rs/pull/1249))
+
+### IMPROVEMENTS
+
+- `[tendermint-light-client-js]` Switch to serde-wasm-bindgen for marshalling
+  JS values ([#1242](https://github.com/informalsystems/tendermint-rs/pull/1242))
+
+### SECURITY
+
+- `[tendermint-light-client]` Fix an issue where the light client was not
+  checking that the chain ID of the trusted and untrusted headers match
+  ([#1249](https://github.com/informalsystems/tendermint-rs/pull/1249))
+
 ## v0.27.0
 
 *Nov 28, 2022*
```

### abci/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name        = "tendermint-abci"
-version     = "0.27.0"
+version     = "0.28.0"
 authors     = ["Informal Systems <hello@informal.systems>"]
 edition     = "2018"
 license     = "Apache-2.0"
@@ -33,7 +33,7 @@ binary = [
 [dependencies]
 bytes = { version = "1.0", default-features = false }
 prost = { version = "0.11", default-features = false }
-tendermint-proto = { version = "0.27.0", default-features = false, path = "../proto" }
+tendermint-proto = { version = "0.28.0", default-features = false, path = "../proto" }
 tracing = { version = "0.1", default-features = false }
 flex-error = { version = "0.4.4", default-features = false }
 structopt = { version = "0.3", optional = true, default-features = false }
```

### config/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name       = "tendermint-config"
-version    = "0.27.0" # Also update `html_root_url` in lib.rs and
+version    = "0.28.0" # Also update `html_root_url` in lib.rs and
                                # depending crates (rpc, light-node, ..) when bumping this
 license    = "Apache-2.0"
 homepage   = "https://www.tendermint.com/"
@@ -25,7 +25,7 @@ all-features = true
 rustdoc-args = ["--cfg", "docsrs"]
 
 [dependencies]
-tendermint = { version = "0.27.0", default-features = false, path = "../tendermint" }
+tendermint = { version = "0.28.0", default-features = false, path = "../tendermint" }
 flex-error = { version = "0.4.4", default-features = false }
 serde = { version = "1", features = ["derive"] }
 serde_json = "1"
```

### light-client-js/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name        = "tendermint-light-client-js"
-version     = "0.27.0"
+version     = "0.28.0"
 authors     = ["Informal Systems <hello@informal.systems>"]
 edition     = "2018"
 license     = "Apache-2.0"
@@ -22,8 +22,8 @@ default = ["console_error_panic_hook"]
 [dependencies]
 serde = { version = "1.0", default-features = false, features = [ "derive" ] }
 serde_json = { version = "1.0", default-features = false }
-tendermint = { version = "0.27.0", default-features = false, path = "../tendermint" }
-tendermint-light-client-verifier = { version = "0.27.0", default-features = false, path = "../light-client-verifier" }
+tendermint = { version = "0.28.0", default-features = false, path = "../tendermint" }
+tendermint-light-client-verifier = { version = "0.28.0", default-features = false, path = "../light-client-verifier" }
 wasm-bindgen = { version = "0.2.63", default-features = false, features = [ "serde-serialize" ] }
 serde-wasm-bindgen = { version = "0.4.5", default-features = false }
 
```

### light-client-verifier/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name       = "tendermint-light-client-verifier"
-version    = "0.27.0"
+version    = "0.28.0"
 edition    = "2021"
 license    = "Apache-2.0"
 readme     = "README.md"
@@ -26,7 +26,7 @@ rustdoc-args = ["--cfg", "docsrs"]
 default = ["flex-error/std", "flex-error/eyre_tracer"]
 
 [dependencies]
-tendermint = { version = "0.27.0", path = "../tendermint", default-features = false }
+tendermint = { version = "0.28.0", path = "../tendermint", default-features = false }
 
 derive_more = { version = "0.99.5", default-features = false, features = ["display"] }
 serde = { version = "1.0.106", default-features = false }
```

### light-client-verifier/src/errors.rs
```diff
@@ -112,6 +112,16 @@ define_error! {
                     e.got, e.expected)
             },
 
+        ChainIdMismatch
+            {
+                got: String,
+                expected: String,
+            }
+            | e | {
+                format_args!("chain-id mismatch: got={0} expected={1}",
+                    e.got, e.expected)
+            },
+
         NonMonotonicBftTime
             {
                 header_bft_time: Time,
```

### light-client-verifier/src/predicates.rs
```diff
@@ -2,7 +2,7 @@
 
 use core::time::Duration;
 
-use tendermint::{block::Height, hash::Hash};
+use tendermint::{block::Height, chain::Id as ChainId, hash::Hash};
 
 use crate::{
     errors::VerificationError,
@@ -160,6 +160,22 @@ pub trait VerificationPredicates: Send + Sync {
         }
     }
 
+    /// Check that the chain-ids of the trusted header and the untrusted one are the same
+    fn is_matching_chain_id(
+        &self,
+        untrusted_chain_id: &ChainId,
+        trusted_chain_id: &ChainId,
+    ) -> Result<(), VerificationError> {
+        if untrusted_chain_id == trusted_chain_id {
+            Ok(())
+        } else {
+            Err(VerificationError::chain_id_mismatch(
+                untrusted_chain_id.to_string(),
+                trusted_chain_id.to_string(),
+            ))
+        }
+    }
+
     /// Check that there is enough validators overlap between the trusted validator set
     /// and the untrusted signed header.
     fn has_sufficient_validators_overlap(
@@ -282,6 +298,30 @@ mod tests {
         }
     }
 
+    #[test]
+    fn test_is_matching_chain_id() {
+        let val = vec![Validator::new("val-1")];
+        let header_one = Header::new(&val).chain_id("chaina-1").generate().unwrap();
+        let header_two = Header::new(&val).chain_id("chainb-1").generate().unwrap();
+
+        let vp = ProdPredicates::default();
+
+        // 1. ensure valid header verifies
+        let result_ok = vp.is_matching_chain_id(&header_one.chain_id, &header_one.chain_id);
+        assert!(result_ok.is_ok());
+
+        // 2. ensure header with different chain-id fails
+        let result_err = vp.is_matching_chain_id(&header_one.chain_id, &header_two.chain_id);
+
+        match result_err {
+            Err(VerificationError(VerificationErrorDetail::ChainIdMismatch(e), _)) => {
+                assert_eq!(e.got, header_one.chain_id.to_string());
+                assert_eq!(e.expected, header_two.chain_id.to_string());
+            },
+            _ => panic!("expected ChainIdMismatch error"),
+        }
+    }
+
     #[test]
     fn test_is_within_trust_period() {
         let val = Validator::new("val-1");
```
