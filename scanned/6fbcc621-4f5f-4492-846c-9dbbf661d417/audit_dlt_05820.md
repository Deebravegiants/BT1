# [?] chore: use latest wasmtime security patch (#15663)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-05-04
Source: https://github.com/near/nearcore/commit/d1f5a0f949a83f25d67729906aacec9b731c25b8
Type: security-commit

## Details
chore: use latest wasmtime security patch (#15663)

Update from wasmtime 36.0.7 to 36.0.8.

Related crates from the same monorepo are updated, too.

This includes a fix for a security advisory:
https://rustsec.org/advisories/RUSTSEC-2026-0114

We have `memory64` disabled, so we are not actually affected.

However, since we have not released anything with
Wasmtime, yet, it is still easy to update.
I don't really see a reason not to do it.

## Patch
### Cargo.lock
```diff
@@ -1326,46 +1326,46 @@ dependencies = [
 
 [[package]]
 name = "cranelift-assembler-x64"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c8056d63fef9a6f88a1e7aae52bb08fcf48de8866d514c0dc52feb15975f5db5"
+checksum = "cb1ffe339f197d6645b4d3037edf67c13cd3aa8871f29c2c9c046c729c1b9a17"
 dependencies = [
  "cranelift-assembler-x64-meta",
 ]
 
 [[package]]
 name = "cranelift-assembler-x64-meta"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "57d063b40884a0d733223a45c5de1155395af4393cf7f900d5be8e2cbc094015"
+checksum = "1e81a21df73d1b12ed19eba481c08de8891e179e1870ed28d6e397f7746108f5"
 dependencies = [
  "cranelift-srcgen",
 ]
 
 [[package]]
 name = "cranelift-bforest"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3c3add2881bae2d55cd7162906988dd70053cb7ece865ad793a6754b04d47df6"
+checksum = "3cf917d0180c15c945c13c8dde615d32a015769513b29158f728311d85a8f80d"
 dependencies = [
  "cranelift-entity",
 ]
 
 [[package]]
 name = "cranelift-bitset"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dd73e32bc1ea4bddc4c770760c66fa24b2890991b0561af554219e603fcd7c34"
+checksum = "a6f4e1af2df00798c2895d228bb53d65c5aa09acace8525096f0b53830ffe42c"
 dependencies = [
  "serde",
  "serde_derive",
 ]
 
 [[package]]
 name = "cranelift-codegen"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3e1da85f2636fe28244848861d1ed0f8dccdc6e98fc5db31aa5eb8878e7ff617"
+checksum = "4e3a5d7300e4b44933dcf2947399945abe3f30f92c789b496ad72949e3ee15a6"
 dependencies = [
  "bumpalo",
  "cranelift-assembler-x64",
@@ -1390,9 +1390,9 @@ dependencies = [
 
 [[package]]
 name = "cranelift-codegen-meta"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ee3c8aba9d89832df27364b2e79dc2fe288daf4bd6c7347829e7f3f258ea5650"
+checksum = "becdb5c3111800d7f8e666fe5f35693bfc77de4401bfcaea19815caf7c482fb9"
 dependencies = [
  "cranelift-assembler-x64-meta",
  "cranelift-codegen-shared",
@@ -1403,24 +1403,24 @@ dependencies = [
 
 [[package]]
 name = "cranelift-codegen-shared"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ac9a9b09fe107fef6377caed20614586124184cffccb73611312ceb922a917e6"
+checksum = "d8fa77efffa12934971f757e154b16dd5e369a7f388a0f3adff74aadfd4c5a1d"
 
 [[package]]
 name = "cranelift-control"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "50aef001c7ad250d5fdda2c7481cbfcabe6435c66106adf5760dcb9fb9a8ede4"
+checksum = "62441d3aae3372381e03a121880482158ce90ca3bc2a56607cc122ee07536fe4"
 dependencies = [
  "arbitrary",
 ]
 
 [[package]]
 name = "cranelift-entity"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cf3c84656a010df2b5afaedcbbbd94f1efe175b55e29864df7b99e64bfa40d56"
+checksum = "7bdc9832a010e0d411439aa016e1664dd23ca5c8953bf26b90fe34ad4b76822d"
 dependencies = [
  "cranelift-bitset",
  "serde",
@@ -1429,9 +1429,9 @@ dependencies = [
 
 [[package]]
 name = "cranelift-frontend"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6aa1d2006915cddb63705db46dcfb8637fe08f91d26fbe59680d7257ec39d609"
+checksum = "9530b689b7c3accdbb32263ca318e19ab3bcf616d3a160c8456537c99b4c565b"
 dependencies = [
  "cranelift-codegen",
  "log",
@@ -1441,15 +1441,15 @@ dependencies = [
 
 [[package]]
 name = "cranelift-isle"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6e4fecbcbb81273f9aff4559e26fc341f42663da420cca5ac84b34e74e9267e0"
+checksum = "3fcd3258a4d87376f2681c72269a42009286a3d3707b2af4024ba5b3750ad477"
 
 [[package]]
 name = "cranelift-native"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "976a3d85f197a56ae34ee4d5a5e469855ac52804a09a513d0562d425da0ff56e"
+checksum = "642c5703a22b58abccbf46f46c0dae65f0535bbe725beec70527a1ffcbbc1d34"
 dependencies = [
  "cranelift-codegen",
  "libc",
@@ -1458,9 +1458,9 @@ dependencies = [
 
 [[package]]
 name = "cranelift-srcgen"
-version = "0.123.7"
+version = "0.123.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "37fbd4aefce642145491ff862d2054a71b63d2d97b8dd1e280c9fdaf399598b7"
+checksum = "d200dcd5a37de108ec1329e0ba924e2badd2c0ef2343c338310135159ae454e2"
 
 [[package]]
 name = "crc"
@@ -6628,9 +6628,9 @@ dependencies = [
 
 [[package]]
 name = "pulley-interpreter"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a078b4bdfd275fadeefc4f9ae3675ee5af302e69497da439956dd05257858970"
+checksum = "35eaba3163b9faf1d707f0704a7370bfdbe73622c766acdaf1fa4addb87510de"
 dependencies = [
  "cranelift-bitset",
  "log",
@@ -6640,9 +6640,9 @@ dependencies = [
 
 [[package]]
 name = "pulley-macros"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9dac91999883fd00b900eb5377be403c5cb8b93e10efcb571bf66454c2d9f231"
+checksum = "ac294897a29ce07919714f9f25c11a819d75759d47eb9f3273845ffea5a5760d"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -9479,9 +9479,9 @@ dependencies = [
 
 [[package]]
 name = "wasmtime"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b80d5ba38b9b00f60a0665e07dde38e91d884d4a78cd61d777c8cf081a1267c1"
+checksum = "2060d93be880840d764ab537464b916e22c07758ac5d43e5f07cc86fec6d1bec"
 dependencies = [
  "addr2line 0.25.0",
  "anyhow",
@@ -9521,9 +9521,9 @@ dependencies = [
 
 [[package]]
 name = "wasmtime-environ"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "44a45d60dea98308decb71a9f7bb35a629696d1fbf7127dbfde42cbc64b8fa33"
+checksum = "902f991ca8c2e5abc03119eb5d7f7f57da1b7c2123addb8214b49c188737711e"
 dependencies = [
  "anyhow",
  "cranelift-bitset",
@@ -9544,18 +9544,18 @@ dependencies = [
 
 [[package]]
 name = "wasmtime-internal-asm-macros"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dd014b4001b6da03d79062d9ad5ec98fa62e34d50e30e46298545282cc2957e4"
+checksum = "b02cec619b54ce7652d1d7676718a42ccf5f16b2fb23c27cd6e3c307bc93907a"
 dependencies = [
  "cfg-if",
 ]
 
 [[package]]
 name = "wasmtime-internal-cranelift"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4047020866a80aa943e41133e607020e17562126cf81533362275272098a22b1"
+checksum = "54eb7fc20c8692dc96148365d7a00a1b79fee810833c75bdf8ec073a46e4721a"
 dependencies = [
  "anyhow",
  "cfg-if",
@@ -9580,9 +9580,9 @@ dependencies = [
 
 [[package]]
 name = "wasmtime-internal-fiber"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7cd172b622993bb8f834f6ca3b7683dfdba72b12db0527824850fdec17c89e5a"
+checksum = "30708e122dcc1e175c66345c209c01752ca0cd20c9021721b6f56968342e9dbe"
 dependencies = [
  "anyhow",
  "cc",
@@ -9596,19 +9596,19 @@ dependencies = [
 
 [[package]]
 name = "wasmtime-internal-jit-debug"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1287e310fef4c8759a6b5caa0d44eff9a03ebcd6c273729cc39ce3e321a9e26a"
+checksum = "1eeaab071a646d9ae205266adf186c63fa6d077d36b0b33628dd6c3d321d3195"
 dependencies = [
  "cc",
  "wasmtime-internal-versioned-export-macros",
 ]
 
 [[package]]
 name = "wasmtime-internal-jit-icache-coherence"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c02bca30ef670a31496d742d9facdbd0228debe766b1e9541655c0530ff5c953"
+checksum = "09979561e6e4a17bf55722463b066ccb968f010ac6ec5d647e4dff19eddbb19e"
 dependencies = [
  "anyhow",
  "cfg-if",
@@ -9618,24 +9618,24 @@ dependencies = [
 
 [[package]]
 name = "wasmtime-internal-math"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fd3a1f51a037ae2c048f0d76d36e27f0d22276295496c44f16a251f24690e003"
+checksum = "9193eb852e5c68aeb95a5ea7538c2bec503023169a0b24430224b4f1ded24988"
 dependencies = [
  "libm",
 ]
 
 [[package]]
 name = "wasmtime-internal-slab"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ba6171aac3d66e4d69e50080bb6bc5205de2283513984a4118a93cb66dc02994"
+checksum = "289bfa4fbb43f406f36166737f1f25522c215ef2ef11f98423089a6a7590a3d1"
 
 [[package]]
 name = "wasmtime-internal-unwinder"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3fd1bc1783391a02176fb687159b1779fc10b71d5350adf09c1f3aa8442a02cc"
+checksum = "4e748c970993865d9bf474465c3f10f96e541c472bc8f7ec0b031779f4ac29c6"
 dependencies = [
  "anyhow",
  "cfg-if",
@@ -9646,9 +9646,9 @@ dependencies = [
 
 [[package]]
 name = "wasmtime-internal-versioned-export-macros"
-version = "36.0.7"
+version = "36.0.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8097e2c8ca02ed65d31dda111faa0888ffbf28dc3ee74355e283118a8d293eb0"
+checksum = "e97e07438cb8b50df3bc9659c56757830a15235c94268dbbd54186524fd4ed84"
 dependencies = [
  "proc-macro2",
  "quote",
```

### runtime/near-vm-runner/src/tests/cache.rs
```diff
@@ -239,13 +239,13 @@ fn test_wasmtime_artifact_output_stability() {
     ];
     let compiled_hashes = [
         // See the above comment if you want to change this
-        17467356520024489490,
-        14729060831070184139,
-        11041498883632407283,
-        12049699321754363033,
-        9906436427985886682,
-        15560032392659795845,
-        11171783944424554209,
+        8872655251928162472,
+        5874696682778417150,
+        15325374922549829539,
+        16384246902307889877,
+        10198860491477346864,
+        17647195016507989234,
+        9026912712981131179,
     ];
     let mut got_prepared_hashes = Vec::with_capacity(seeds.len());
     let mut got_compiled_hashes = Vec::with_capacity(seeds.len());
@@ -327,7 +327,7 @@ fn test_wasmtime_sparse_contract_stability() {
     // sparse-data-segment case that `arbitrary_contract` does not cover.
     // See comments on that test for how to update these hashes.
     let expected_prepared_hash: u64 = 16694328674582109973;
-    let expected_compiled_hash: u64 = 8543849532946659263;
+    let expected_compiled_hash: u64 = 3829876428286564557;
 
     let contract = ContractCode::new(sparse_wasm_contract(), None);
     let config = test_vm_config(Some(VMKind::Wasmtime));
```

### runtime/near-vm-runner/src/wasmtime_runner/mod.rs
```diff
@@ -469,7 +469,7 @@ impl WasmtimeVM {
     pub(crate) fn vm_hash(&self) -> u64 {
         // increment the `version` when making modifications that affect the
         // artifact compatibility.
-        let version = 71;
+        let version = 72;
 
         let mut hasher = std::hash::DefaultHasher::new();
         self.engine.precompile_compatibility_hash().hash(&mut hasher);
```
