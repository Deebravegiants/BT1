# [?] enclave: Tmp fix the crash calling rand::thread_rng

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2021-08-27
Source: https://github.com/Phala-Network/phala-blockchain/commit/5ec71af30e02ef9b14f1a6892ba4c1c2e0275d18
Type: security-commit

## Details
enclave: Tmp fix the crash calling rand::thread_rng

## Patch
### standalone/pruntime/enclave/src/lib.rs
```diff
@@ -811,9 +811,9 @@ fn load_secret_keys() -> Result<PersistentRuntimeData> {
 }
 
 fn new_sr25519_key() -> sr25519::Pair {
-    let mut rng = rand::thread_rng();
+    let rand = ring::rand::SystemRandom::new();
     let mut seed = [0_u8; SEED_BYTES];
-    rng.fill_bytes(&mut seed);
+    rand.fill(&mut seed).unwrap();
     sr25519::Pair::from_seed(&seed)
 }
 
```

### standalone/pruntime/enclave/src/prpc_service.rs
```diff
@@ -319,12 +319,12 @@ pub fn init_runtime(
 
     let mut cpu_feature_level: u32 = 1;
     // Atom doesn't support AVX
-    if is_x86_feature_detected!("avx2") {
+    if sgx_trts::is_x86_feature_detected!("avx2") {
         info!("CPU Support AVX2");
         cpu_feature_level += 1;
 
         // Customer-level Core doesn't support AVX512
-        if is_x86_feature_detected!("avx512f") {
+        if sgx_trts::is_x86_feature_detected!("avx512f") {
             info!("CPU Support AVX512");
             cpu_feature_level += 1;
         }
```
