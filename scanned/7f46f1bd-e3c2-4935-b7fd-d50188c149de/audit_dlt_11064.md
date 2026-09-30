# [?] fix(libzkp): try to convert to string for panic errors (#949)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2023-09-19
Source: https://github.com/scroll-tech/scroll/commit/f0920362c54fba1a2fdb79650c57d33b9693f2cb
Type: security-commit

## Details
fix(libzkp): try to convert to string for panic errors (#949)

## Patch
### common/libzkp/impl/src/batch.rs
```diff
@@ -1,7 +1,8 @@
 use crate::{
     types::{CheckChunkProofsResponse, ProofResult},
     utils::{
-        c_char_to_str, c_char_to_vec, file_exists, string_to_c_char, vec_to_c_char, OUTPUT_DIR,
+        c_char_to_str, c_char_to_vec, file_exists, panic_catch, string_to_c_char, vec_to_c_char,
+        OUTPUT_DIR,
     },
 };
 use libc::c_char;
@@ -11,7 +12,7 @@ use prover::{
     utils::{chunk_trace_to_witness_block, init_env_and_log},
     BatchProof, BlockTrace, ChunkHash, ChunkProof,
 };
-use std::{cell::OnceCell, env, panic, ptr::null};
+use std::{cell::OnceCell, env, ptr::null};
 
 static mut PROVER: OnceCell<Prover> = OnceCell::new();
 static mut VERIFIER: OnceCell<Verifier> = OnceCell::new();
@@ -55,7 +56,7 @@ pub unsafe extern "C" fn init_batch_verifier(params_dir: *const c_char, assets_d
 /// # Safety
 #[no_mangle]
 pub unsafe extern "C" fn get_batch_vk() -> *const c_char {
-    let vk_result = panic::catch_unwind(|| PROVER.get_mut().unwrap().get_vk());
+    let vk_result = panic_catch(|| PROVER.get_mut().unwrap().get_vk());
 
     vk_result
         .ok()
@@ -66,7 +67,7 @@ pub unsafe extern "C" fn get_batch_vk() -> *const c_char {
 /// # Safety
 #[no_mangle]
 pub unsafe extern "C" fn check_chunk_proofs(chunk_proofs: *const c_char) -> *const c_char {
-    let check_result: Result<bool, String> = panic::catch_unwind(|| {
+    let check_result: Result<bool, String> = panic_catch(|| {
         let chunk_proofs = c_char_to_vec(chunk_proofs);
         let chunk_proofs = serde_json::from_slice::<Vec<ChunkProof>>(&chunk_proofs)
             .map_err(|e| format!("failed to deserialize chunk proofs: {e:?}"))?;
@@ -102,7 +103,7 @@ pub unsafe extern "C" fn gen_batch_proof(
     chunk_hashes: *const c_char,
     chunk_proofs: *const c_char,
 ) -> *const c_char {
-    let proof_result: Result<Vec<u8>, String> = panic::catch_unwind(|| {
+    let proof_result: Result<Vec<u8>, String> = panic_catch(|| {
         let chunk_hashes = c_char_to_vec(chunk_hashes);
         let chunk_proofs = c_char_to_vec(chunk_proofs);
 
@@ -151,7 +152,7 @@ pub unsafe extern "C" fn verify_batch_proof(proof: *const c_char) -> c_char {
     let proof = c_char_to_vec(proof);
     let proof = serde_json::from_slice::<BatchProof>(proof.as_slice()).unwrap();
 
-    let verified = panic::catch_unwind(|| VERIFIER.get().unwrap().verify_agg_evm_proof(proof));
+    let verified = panic_catch(|| VERIFIER.get().unwrap().verify_agg_evm_proof(proof));
     verified.unwrap_or(false) as c_char
 }
 
```

### common/libzkp/impl/src/chunk.rs
```diff
@@ -1,7 +1,8 @@
 use crate::{
     types::ProofResult,
     utils::{
-        c_char_to_str, c_char_to_vec, file_exists, string_to_c_char, vec_to_c_char, OUTPUT_DIR,
+        c_char_to_str, c_char_to_vec, file_exists, panic_catch, string_to_c_char, vec_to_c_char,
+        OUTPUT_DIR,
     },
 };
 use libc::c_char;
@@ -11,7 +12,7 @@ use prover::{
     zkevm::{Prover, Verifier},
     BlockTrace, ChunkProof,
 };
-use std::{cell::OnceCell, env, panic, ptr::null};
+use std::{cell::OnceCell, env, ptr::null};
 
 static mut PROVER: OnceCell<Prover> = OnceCell::new();
 static mut VERIFIER: OnceCell<Verifier> = OnceCell::new();
@@ -55,7 +56,7 @@ pub unsafe extern "C" fn init_chunk_verifier(params_dir: *const c_char, assets_d
 /// # Safety
 #[no_mangle]
 pub unsafe extern "C" fn get_chunk_vk() -> *const c_char {
-    let vk_result = panic::catch_unwind(|| PROVER.get_mut().unwrap().get_vk());
+    let vk_result = panic_catch(|| PROVER.get_mut().unwrap().get_vk());
 
     vk_result
         .ok()
@@ -66,7 +67,7 @@ pub unsafe extern "C" fn get_chunk_vk() -> *const c_char {
 /// # Safety
 #[no_mangle]
 pub unsafe extern "C" fn gen_chunk_proof(block_traces: *const c_char) -> *const c_char {
-    let proof_result: Result<Vec<u8>, String> = panic::catch_unwind(|| {
+    let proof_result: Result<Vec<u8>, String> = panic_catch(|| {
         let block_traces = c_char_to_vec(block_traces);
         let block_traces = serde_json::from_slice::<Vec<BlockTrace>>(&block_traces)
             .map_err(|e| format!("failed to deserialize block traces: {e:?}"))?;
@@ -101,6 +102,6 @@ pub unsafe extern "C" fn verify_chunk_proof(proof: *const c_char) -> c_char {
     let proof = c_char_to_vec(proof);
     let proof = serde_json::from_slice::<ChunkProof>(proof.as_slice()).unwrap();
 
-    let verified = panic::catch_unwind(|| VERIFIER.get().unwrap().verify_chunk_proof(proof));
+    let verified = panic_catch(|| VERIFIER.get().unwrap().verify_chunk_proof(proof));
     verified.unwrap_or(false) as c_char
 }
```

### common/libzkp/impl/src/utils.rs
```diff
@@ -3,6 +3,7 @@ use std::{
     env,
     ffi::{CStr, CString},
     os::raw::c_char,
+    panic::{catch_unwind, AssertUnwindSafe},
     path::PathBuf,
 };
 
@@ -34,3 +35,15 @@ pub(crate) fn file_exists(dir: &str, filename: &str) -> bool {
 
     path.exists()
 }
+
+pub(crate) fn panic_catch<F: FnOnce() -> R, R>(f: F) -> Result<R, String> {
+    catch_unwind(AssertUnwindSafe(f)).map_err(|err| {
+        if let Some(s) = err.downcast_ref::<String>() {
+            s.to_string()
+        } else if let Some(s) = err.downcast_ref::<&str>() {
+            s.to_string()
+        } else {
+            format!("unable to get panic info {err:?}")
+        }
+    })
+}
```
