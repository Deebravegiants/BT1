# [?] fix: ecdsa recovery failure may cause executor to panic (#1799)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2024-11-19
Source: https://github.com/succinctlabs/sp1/commit/3bbf4cff10b43f4e85d07d91535d719cfc046c8d
Type: security-commit

## Details
fix: ecdsa recovery failure may cause executor to panic (#1799)

## Patch
### Cargo.lock
```diff
@@ -6862,7 +6862,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-build"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "anyhow",
  "cargo_metadata",
@@ -6873,7 +6873,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-cli"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "anstyle",
  "anyhow",
@@ -6901,7 +6901,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-core-executor"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "bincode",
  "bytemuck",
@@ -6934,7 +6934,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-core-machine"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "bincode",
  "cfg-if",
@@ -6983,7 +6983,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-cuda"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "bincode",
  "ctrlc",
@@ -7000,7 +7000,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-curves"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "cfg-if",
  "curve25519-dalek",
@@ -7022,15 +7022,15 @@ dependencies = [
 
 [[package]]
 name = "sp1-derive"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "quote",
  "syn 1.0.109",
 ]
 
 [[package]]
 name = "sp1-eval"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "anyhow",
  "bincode",
@@ -7050,7 +7050,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-helper"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "sp1-build",
 ]
@@ -7067,15 +7067,15 @@ dependencies = [
 
 [[package]]
 name = "sp1-lib"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "bincode",
  "serde",
 ]
 
 [[package]]
 name = "sp1-perf"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "anyhow",
  "bincode",
@@ -7097,7 +7097,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-primitives"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "bincode",
  "hex",
@@ -7113,7 +7113,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-prover"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "anyhow",
  "bincode",
@@ -7153,7 +7153,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-recursion-circuit"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "ff 0.13.0",
  "hashbrown 0.14.5",
@@ -7189,7 +7189,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-recursion-compiler"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "backtrace",
  "criterion",
@@ -7214,7 +7214,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-recursion-core"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "backtrace",
  "ff 0.13.0",
@@ -7249,15 +7249,15 @@ dependencies = [
 
 [[package]]
 name = "sp1-recursion-derive"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "quote",
  "syn 1.0.109",
 ]
 
 [[package]]
 name = "sp1-recursion-gnark-cli"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "bincode",
  "clap",
@@ -7266,7 +7266,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-recursion-gnark-ffi"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "anyhow",
  "bincode",
@@ -7290,7 +7290,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-sdk"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "alloy-primitives 0.8.11",
  "alloy-signer",
@@ -7336,7 +7336,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-stark"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "arrayref",
  "getrandom 0.2.15",
@@ -7371,7 +7371,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-verifier"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "hex",
  "lazy_static",
@@ -7385,7 +7385,7 @@ dependencies = [
 
 [[package]]
 name = "sp1-zkvm"
-version = "3.2.1"
+version = "3.3.0"
 dependencies = [
  "cfg-if",
  "getrandom 0.2.15",
@@ -7395,7 +7395,7 @@ dependencies = [
  "p3-field",
  "rand 0.8.5",
  "sha2 0.10.8",
- "sp1-lib 3.2.1",
+ "sp1-lib 3.3.0",
  "sp1-primitives",
 ]
 
```

### Cargo.toml
```diff
@@ -1,5 +1,5 @@
 [workspace.package]
-version = "3.2.1"
+version = "3.3.0"
 edition = "2021"
 license = "MIT OR Apache-2.0"
 repository = "https://github.com/succinctlabs/sp1"
@@ -47,26 +47,26 @@ debug-assertions = true
 
 [workspace.dependencies]
 # sp1
-sp1-build = { path = "crates/build", version = "3.2.1" }
-sp1-cli = { path = "crates/cli", version = "3.2.1", default-features = false }
-sp1-core-machine = { path = "crates/core/machine", version = "3.2.1" }
-sp1-core-executor = { path = "crates/core/executor", version = "3.2.1" }
-sp1-curves = { path = "crates/curves", version = "3.2.1" }
-sp1-derive = { path = "crates/derive", version = "3.2.1" }
-sp1-eval = { path = "crates/eval", version = "3.2.1" }
-sp1-helper = { path = "crates/helper", version = "3.2.1", default-features = false }
-sp1-primitives = { path = "crates/primitives", version = "3.2.1" }
-sp1-prover = { path = "crates/prover", version = "3.2.1" }
-sp1-recursion-compiler = { path = "crates/recursion/compiler", version = "3.2.1" }
-sp1-recursion-core = { path = "crates/recursion/core", version = "3.2.1", default-features = false }
-sp1-recursion-derive = { path = "crates/recursion/derive", version = "3.2.1", default-features = false }
-sp1-recursion-gnark-ffi = { path = "crates/recursion/gnark-ffi", version = "3.2.1", default-features = false }
-sp1-recursion-circuit = { path = "crates/recursion/circuit", version = "3.2.1", default-features = false }
-sp1-sdk = { path = "crates/sdk", version = "3.2.1" }
-sp1-cuda = { path = "crates/cuda", version = "3.2.1" }
-sp1-stark = { path = "crates/stark", version = "3.2.1" }
-sp1-lib = { path = "crates/zkvm/lib", version = "3.2.1", default-features = false }
-sp1-zkvm = { path = "crates/zkvm/entrypoint", version = "3.2.1", default-features = false }
+sp1-build = { path = "crates/build", version = "3.3.0" }
+sp1-cli = { path = "crates/cli", version = "3.3.0", default-features = false }
+sp1-core-machine = { path = "crates/core/machine", version = "3.3.0" }
+sp1-core-executor = { path = "crates/core/executor", version = "3.3.0" }
+sp1-curves = { path = "crates/curves", version = "3.3.0" }
+sp1-derive = { path = "crates/derive", version = "3.3.0" }
+sp1-eval = { path = "crates/eval", version = "3.3.0" }
+sp1-helper = { path = "crates/helper", version = "3.3.0", default-features = false }
+sp1-primitives = { path = "crates/primitives", version = "3.3.0" }
+sp1-prover = { path = "crates/prover", version = "3.3.0" }
+sp1-recursion-compiler = { path = "crates/recursion/compiler", version = "3.3.0" }
+sp1-recursion-core = { path = "crates/recursion/core", version = "3.3.0", default-features = false }
+sp1-recursion-derive = { path = "crates/recursion/derive", version = "3.3.0", default-features = false }
+sp1-recursion-gnark-ffi = { path = "crates/recursion/gnark-ffi", version = "3.3.0", default-features = false }
+sp1-recursion-circuit = { path = "crates/recursion/circuit", version = "3.3.0", default-features = false }
+sp1-sdk = { path = "crates/sdk", version = "3.3.0" }
+sp1-cuda = { path = "crates/cuda", version = "3.3.0" }
+sp1-stark = { path = "crates/stark", version = "3.3.0" }
+sp1-lib = { path = "crates/zkvm/lib", version = "3.3.0", default-features = false }
+sp1-zkvm = { path = "crates/zkvm/entrypoint", version = "3.3.0", default-features = false }
 
 # p3
 p3-air = "0.1.4-succinct"
```

### book/writing-programs/patched-crates.md
```diff
@@ -39,6 +39,9 @@ tiny-keccak = { git = "https://github.com/sp1-patches/tiny-keccak", tag = "tiny_
 curve25519-dalek = { git = "https://github.com/sp1-patches/curve25519-dalek", tag = "curve25519_dalek-v4.1.3-patch-v1" }
 curve25519-dalek-ng = { git = "https://github.com/sp1-patches/curve25519-dalek-ng", tag = "curve25519_dalek_ng-v4.1.1-patch-v1" }
 ed25519-consensus = { git = "https://github.com/sp1-patches/ed25519-consensus", tag = "ed25519_consensus-v2.1.0-patch-v1" }
+# For sp1 versions >= 3.3.0
+ecdsa-core = { git = "https://github.com/sp1-patches/signatures", package = "ecdsa", tag = "ecdsa-v0.16.9-patch-v3.3.0" }
+# For sp1 versions < 3.3.0
 ecdsa-core = { git = "https://github.com/sp1-patches/signatures", package = "ecdsa", tag = "ecdsa-v0.16.9-patch-v1" }
 secp256k1 = { git = "https://github.com/sp1-patches/rust-secp256k1", tag = "secp256k1-v0.29.0-patch-v1" }
 substrate-bn = { git = "https://github.com/sp1-patches/bn", tag = "substrate_bn-v0.6.0-patch-v1" }
```

### crates/core/executor/src/hook.rs
```diff
@@ -13,6 +13,11 @@ pub type BoxedHook<'a> = Arc<RwLock<dyn Hook + Send + Sync + 'a>>;
 /// The file descriptor through which to access `hook_ecrecover`.
 pub const FD_ECRECOVER_HOOK: u32 = 5;
 
+// Note: we skip 6 because we have an eddsa hook in dev.
+
+/// The file descriptor through which to access `hook_ecrecover_2`.
+pub const FD_ECRECOVER_HOOK_2: u32 = 7;
+
 /// A runtime hook. May be called during execution by writing to a specified file descriptor,
 /// accepting and returning arbitrary data.
 pub trait Hook {
@@ -76,6 +81,7 @@ impl<'a> Default for HookRegistry<'a> {
             // Note: To ensure any `fd` value is synced with `zkvm/precompiles/src/io.rs`,
             // add an assertion to the test `hook_fds_match` below.
             (FD_ECRECOVER_HOOK, hookify(hook_ecrecover)),
+            (FD_ECRECOVER_HOOK_2, hookify(hook_ecrecover_v2)),
         ]);
 
         Self { table }
@@ -117,6 +123,7 @@ pub struct HookEnv<'a, 'b: 'a> {
 /// WARNING: This function is used to recover the public key outside of the zkVM context. These
 /// values must be constrained by the zkVM for correctness.
 #[must_use]
+#[deprecated = "Use `hook_ecrecover_v2` instead."]
 pub fn hook_ecrecover(_: HookEnv, buf: &[u8]) -> Vec<Vec<u8>> {
     assert_eq!(buf.len(), 65 + 32, "ecrecover input should have length 65 + 32");
     let (sig, msg_hash) = buf.split_at(65);
@@ -141,6 +148,52 @@ pub fn hook_ecrecover(_: HookEnv, buf: &[u8]) -> Vec<Vec<u8>> {
     vec![bytes.to_vec(), s_inverse.to_bytes().to_vec()]
 }
 
+/// Recovers the public key from the signature and message hash using the k256 crate.
+///
+/// # Arguments
+///
+/// * `env` - The environment in which the hook is invoked.
+/// * `buf` - The buffer containing the signature and message hash.
+///     - The signature is 65 bytes, the first 64 bytes are the signature and the last byte is the
+///       recovery ID.
+///     - The message hash is 32 bytes.
+///
+/// The result is returned as a status and a pair of bytes, where the first 32 bytes are the X coordinate
+/// and the second 32 bytes are the Y coordinate of the decompressed point.
+///
+/// A status of 0 indicates that the public key could not be recovered.
+///
+/// WARNING: This function is used to recover the public key outside of the zkVM context. These
+/// values must be constrained by the zkVM for correctness.
+#[must_use]
+pub fn hook_ecrecover_v2(_: HookEnv, buf: &[u8]) -> Vec<Vec<u8>> {
+    assert_eq!(buf.len(), 65 + 32, "ecrecover input should have length 65 + 32, this is a bug.");
+    let (sig, msg_hash) = buf.split_at(65);
+    let sig: &[u8; 65] = sig.try_into().unwrap();
+    let msg_hash: &[u8; 32] = msg_hash.try_into().unwrap();
+
+    let mut recovery_id = sig[64];
+    let mut sig = Signature::from_slice(&sig[..64]).unwrap();
+
+    if let Some(sig_normalized) = sig.normalize_s() {
+        sig = sig_normalized;
+        recovery_id ^= 1;
+    };
+    let recid = RecoveryId::from_byte(recovery_id).expect("Computed recovery ID is invalid, this is a bug.");
+    
+    // Attempting to recvover the public key has failed, write a 0 to indicate to the caller.
+    let Ok(recovered_key) = VerifyingKey::recover_from_prehash(&msg_hash[..], &sig, recid) else {
+        return vec![vec![0]];
+    };
+
+    let bytes = recovered_key.to_sec1_bytes();
+
+    let (_, s) = sig.split_scalars();
+    let s_inverse = s.invert();
+
+    vec![vec![1], bytes.to_vec(), s_inverse.to_bytes().to_vec()]
+}
+
 #[cfg(test)]
 pub mod tests {
     use super::*;
```

### crates/zkvm/lib/src/io.rs
```diff
@@ -15,6 +15,9 @@ pub const FD_HINT: u32 = 4;
 /// The file descriptor for the `ecreover` hook.
 pub const FD_ECRECOVER_HOOK: u32 = 5;
 
+/// The file descriptor through which to access `hook_ecrecover_2`.
+pub const FD_ECRECOVER_HOOK_2: u32 = 7;
+
 /// A writer that writes to a file descriptor inside the zkVM.
 struct SyscallWriter {
     fd: u32,
```
