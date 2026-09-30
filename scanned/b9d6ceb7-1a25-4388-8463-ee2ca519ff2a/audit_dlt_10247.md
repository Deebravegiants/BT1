# [?] Merge pull request #434 from Phala-Network/fix-pruntime-crash

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2021-08-28
Source: https://github.com/Phala-Network/phala-blockchain/commit/b1ce5d1053d7f67439ecc3e8cc71b4f863f578b9
Type: security-commit

## Details
Merge pull request #434 from Phala-Network/fix-pruntime-crash

Patch ppv-lite86 to avoid detect SIMD with CPUID

## Patch
### .gitmodules
```diff
@@ -7,3 +7,6 @@
 [submodule "standalone/pruntime/enclave-api/proto"]
 	path = standalone/pruntime/enclave-api/proto
 	url = https://github.com/Phala-Network/prpc-protos.git
+[submodule "cryptocorrosion-sgx"]
+	path = cryptocorrosion-sgx
+	url = https://github.com/Phala-Network/cryptocorrosion-sgx.git
```

### cryptocorrosion-sgx
```diff
@@ -0,0 +1 @@
+Subproject commit 9efe783c57ce7dd7a093b48d0fecf4f693dee468
```

### standalone/pruntime/enclave/Cargo.toml
```diff
@@ -23,7 +23,7 @@ sgx_tstd        = { rev = "v1.1.3", git = "https://github.com/apache/teaclave-sg
 [dependencies]
 libc        = "0.2.98"
 log         = "0.4.14"
-env_logger  = "0.9.0"
+env_logger  = { version = "0.9.0", default-features = false, features = ["termcolor"] }
 chrono      = "0.4.19"
 base64      = "0.13.0"
 num-bigint  = "0.4.0"
@@ -86,6 +86,7 @@ sp-core = { package = "sp-core", path = "../../../substrate/primitives/core"}
 fixed = "1.9.0"
 fixed-sqrt = "0.2.4"
 fixed-macro = { version = "1.1", default-features = false, git = "https://github.com/kvinwang/fixed-macro.git" }
+ppv-lite86 = { version = "0.2.10", features = ["phala-sgx"] }
 
 # for diem
 # bcs = { path = "../../../diem/vendor/bcs", version = "0.1.2" }
@@ -103,6 +104,9 @@ default = [
 ]
 tests = []
 
+[patch.crates-io]
+ppv-lite86 = { path = "../../../cryptocorrosion-sgx/utils-simd/ppv-lite86/" }
+
 [patch.'https://github.com/apache/teaclave-sgx-sdk.git']
 # sgx_alloc = { path = "../../../teaclave-sgx-sdk/sgx_alloc" }
 # sgx_backtrace = { path = "../../../teaclave-sgx-sdk/sgx_backtrace" }
```

### standalone/pruntime/enclave/src/lib.rs
```diff
@@ -482,8 +482,8 @@ pub fn create_attestation_report(
     };
 
     let mut quote_nonce = sgx_quote_nonce_t { rand: [0; 16] };
-    let mut os_rng = ring::rand::SystemRandom::new();
-    os_rng.fill(&mut quote_nonce.rand).unwrap();
+    let mut os_rng = rand::thread_rng();
+    os_rng.fill_bytes(&mut quote_nonce.rand);
     info!("rand finished");
     let mut qe_report = sgx_report_t::default();
     const RET_QUOTE_BUF_LEN: u32 = 2048;
@@ -811,9 +811,9 @@ fn load_secret_keys() -> Result<PersistentRuntimeData> {
 }
 
 fn new_sr25519_key() -> sr25519::Pair {
-    let rand = ring::rand::SystemRandom::new();
+    let mut rng = rand::thread_rng();
     let mut seed = [0_u8; SEED_BYTES];
-    rand.fill(&mut seed).unwrap();
+    rng.fill_bytes(&mut seed);
     sr25519::Pair::from_seed(&seed)
 }
 
```

### standalone/pruntime/enclave/src/prpc_service.rs
```diff
@@ -422,10 +422,11 @@ pub fn init_runtime(
             contracts::BTC_LOTTERY,
             contracts::btc_lottery::BtcLottery::new(Some(id_pair.clone()))
         );
-        install_contract!(
-            contracts::WEB3_ANALYTICS,
-            contracts::web3analytics::Web3Analytics::new()
-        );
+        // TODO.kevin: This is temporaryly disabled due to the dependency on CPUID which is not allowed in SGX.
+        // install_contract!(
+        //     contracts::WEB3_ANALYTICS,
+        //     contracts::web3analytics::Web3Analytics::new()
+        // );
         install_contract!(
             contracts::DATA_PLAZA,
             contracts::data_plaza::DataPlaza::new()
```
