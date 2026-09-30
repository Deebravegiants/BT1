# [?] Merge branch 'dev' into core-68-fix-code-not-found-error-panic

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2025-05-28
Source: https://github.com/casper-network/casper-node/commit/8bb821392a6c1b003a62e5b4b4d9ea651145f0c6
Type: security-commit

## Details
Merge branch 'dev' into core-68-fix-code-not-found-error-panic

 Conflicts:
	executor/wasm/Cargo.toml
	smart_contracts/contracts/vm2/vm2-trait/src/lib.rs
	smart_contracts/sdk/src/abi_generator.rs

## Patch
### .github/workflows/publish-global-state-update-gen.yml
```diff
@@ -14,19 +14,15 @@ jobs:
     strategy:
       matrix:
         include:
-          - os: ubuntu-20.04
-            code_name: focal
-#          - os: ubuntu-22.04
-#            code_name: jammy
+          - os: ubuntu-22.04
+            code_name: jammy
 #          - os: ubuntu-24.04
 #            code_name: noble
 
     runs-on: ${{ matrix.os }}
 
     steps:
       - uses: actions/checkout@2541b1294d2704b0964813337f33b291d3f8596b #v3.0.2
-        with:
-          key: ${{ matrix.code_name }}
 
       - name: Configure AWS credentials
         uses: aws-actions/configure-aws-credentials@v4
```

### .github/workflows/publish-release-and-crates.yml
```diff
@@ -14,8 +14,8 @@ jobs:
     strategy:
       matrix:
         include:
-          - os: ubuntu-20.04
-            code_name: focal
+          - os: ubuntu-22.04
+            code_name: jammy
 
     runs-on: ${{ matrix.os }}
 
```

### .github/workflows/push-artifacts.yml
```diff
@@ -16,8 +16,8 @@ jobs:
     strategy:
       matrix:
         include:
-          - os: ubuntu-20.04
-            code_name: focal
+          - os: ubuntu-22.04
+            code_name: jammy
 
     runs-on: ${{ matrix.os }}
 
```

### Cargo.lock
```diff
@@ -65,28 +65,17 @@ version = "2.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "512761e0bb2578dd7380c6baaa0f4ce03e84f95e960231d1dec8bf4d7d6e2627"
 
-[[package]]
-name = "aes"
-version = "0.8.4"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b169f7a6d4742236a0a00c541b845991d0ac43e546831af1249753ab4c3aa3a0"
-dependencies = [
- "cfg-if 1.0.0",
- "cipher",
- "cpufeatures",
-]
-
 [[package]]
 name = "ahash"
-version = "0.8.11"
+version = "0.8.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e89da841a80418a9b391ebaea17f5c112ffaaa96f621d2c285b5174da76b9011"
+checksum = "5a15f179cd60c4584b8a8c596927aadc462e27f2ca70c04e0071964a73ba7a75"
 dependencies = [
  "cfg-if 1.0.0",
- "getrandom 0.2.16",
+ "getrandom 0.3.3",
  "once_cell",
  "version_check",
- "zerocopy 0.7.35",
+ "zerocopy",
 ]
 
 [[package]]
@@ -206,15 +195,6 @@ dependencies = [
  "syn 1.0.109",
 ]
 
-[[package]]
-name = "arbitrary"
-version = "1.4.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dde20b3d026af13f561bdd0f15edf01fc734f0dafcedbaf42bba506a9517f223"
-dependencies = [
- "derive_arbitrary",
-]
-
 [[package]]
 name = "arrayref"
 version = "0.3.9"
@@ -376,7 +356,7 @@ version = "0.70.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f49d8fed880d473ea71efb9bf597651e77201bdd4893efe54c9e5d65ae04ce6f"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "cexpr",
  "clang-sys",
  "itertools 0.13.0",
@@ -413,9 +393,9 @@ checksum = "bef38d45163c2f1dde094a7dfd33ccf595c92905c8f8f4fdc18d06fb1037718a"
 
 [[package]]
 name = "bitflags"
-version = "2.9.0"
+version = "2.9.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5c8214115b7bf84099f1309324e63141d4c5d7cc26862f97a0a857dbefe165bd"
+checksum = "1b8e56985ec62d17e9c1001dc89c88ecd7dc08e47eba5ec7c29c7b5eeecde967"
 
 [[package]]
 name = "blake2"
@@ -513,9 +493,9 @@ dependencies = [
 
 [[package]]
 name = "brotli"
-version = "8.0.0"
+version = "8.0.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cf19e729cdbd51af9a397fb9ef8ac8378007b797f8273cfbfdf45dcaa316167b"
+checksum = "9991eea70ea4f293524138648e41ee89b0b2b12ddef3b255effa43c8056e0e0d"
 dependencies = [
  "alloc-no-stdlib",
  "alloc-stdlib",
@@ -593,9 +573,9 @@ dependencies = [
 
 [[package]]
 name = "bytemuck"
-version = "1.22.0"
+version = "1.23.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b6b1fc10dbac614ebc03540c9dbd60e83887fda27794998c6528f1782047d540"
+checksum = "9134a6ef01ce4b366b50689c94f82c14bc72bc5d0386829828a2e2752ef7958c"
 
 [[package]]
 name = "byteorder"
@@ -609,25 +589,6 @@ version = "1.10.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d71b6127be86fdcfddb610f7182ac57211d4b18a3e9c82eb2d17662f2227ad6a"
 
-[[package]]
-name = "bzip2"
-version = "0.5.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "49ecfb22d906f800d4fe833b6282cf4dc1c298f5057ca0b5445e5c209735ca47"
-dependencies = [
- "bzip2-sys",
-]
-
-[[package]]
-name = "bzip2-sys"
-version = "0.1.13+1.0.8"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "225bff33b2141874fe80d71e07d6eec4f85c5c216453dd96388240f96e1acc14"
-dependencies = [
- "cc",
- "pkg-config",
-]
-
 [[package]]
 name = "call-contract"
 version = "0.1.0"
@@ -668,9 +629,9 @@ dependencies = [
  "anyhow",
  "atty",
  "cargo_metadata 0.19.2",
- "casper-sdk 0.1.0",
- "casper-sdk-sys 0.1.0",
- "clap 4.5.37",
+ "casper-contract-sdk",
+ "casper-contract-sdk-sys",
+ "clap 4.5.38",
  "clap-cargo",
  "crossterm",
  "include_dir",
@@ -721,7 +682,7 @@ dependencies = [
 
 [[package]]
 name = "casper-binary-port"
-version = "1.0.0"
+version = "1.1.0"
 dependencies = [
  "bincode",
  "bytes",
@@ -742,17 +703,75 @@ dependencies = [
 
 [[package]]
 name = "casper-contract"
-version = "5.0.0"
+version = "5.1.0"
 dependencies = [
  "casper-types",
  "hex_fmt",
  "version-sync",
  "wee_alloc",
 ]
 
+[[package]]
+name = "casper-contract-macros"
+version = "0.1.2"
+dependencies = [
+ "blake2-rfc",
+ "casper-contract-sdk-sys",
+ "casper-executor-wasm-common",
+ "darling",
+ "paste",
+ "proc-macro2",
+ "quote",
+ "static_assertions",
+ "syn 2.0.101",
+]
+
+[[package]]
+name = "casper-contract-sdk"
+version = "0.1.2"
+dependencies = [
+ "base16",
+ "bitflags 2.9.1",
+ "bnum",
+ "borsh",
+ "bytes",
+ "casper-contract-macros",
+ "casper-contract-sdk-sys",
+ "casper-executor-wasm-common",
+ "cfg-if 1.0.0",
+ "clap 4.5.38",
+ "const-fnv1a-hash",
+ "impl-trait-for-tuples",
+ "linkme",
+ "once_cell",
+ "rand",
+ "serde",
+ "serde_json",
+ "thiserror 2.0.12",
+]
+
+[[package]]
+name = "casper-contract-sdk-codegen"
+version = "0.1.2"
+dependencies = [
+ "borsh",
+ "casper-contract-sdk",
+ "codegen",
+ "indexmap 2.9.0",
+ "serde",
+ "serde_json",
+ "syn 2.0.101",
+ "tempfile",
+ "trybuild",
+]
+
+[[package]]
+name = "casper-contract-sdk-sys"
+version = "0.1.2"
+
 [[package]]
 name = "casper-engine-test-support"
-version = "8.0.0"
+version = "8.1.0"
 dependencies = [
  "blake2 0.9.2",
  "casper-execution-engine",
@@ -811,7 +830,7 @@ dependencies = [
 
 [[package]]
 name = "casper-execution-engine"
-version = "8.0.0"
+version = "8.1.0"
 dependencies = [
  "anyhow",
  "assert_matches",
@@ -824,7 +843,7 @@ dependencies = [
  "casper-wasm",
  "casper-wasm-utils",
  "casper-wasmi",
- "clap 4.5.37",
+ "clap 4.5.38",
  "criterion",
  "datasize",
  "either",
@@ -852,7 +871,7 @@ dependencies = [
  "strum 0.24.1",
  "tempfile",
  "thiserror 1.0.69",
- "toml 0.8.21",
+ "toml 0.8.22",
  "tracing",
  "uint",
  "walrus",
@@ -861,14 +880,14 @@ dependencies = [
 
 [[package]]
 name = "casper-executor-wasm"
-version = "0.1.0"
+version = "0.1.2"
 dependencies = [
  "base16",
  "blake2 0.10.6",
  "borsh",
  "bytes",
  "casper-execution-engine",
- "casper-executor-wasm-common 0.1.0",
+ "casper-executor-wasm-common",
  "casper-executor-wasm-host",
  "casper-executor-wasm-interface",
  "casper-executor-wasmer-backend",
@@ -887,12 +906,12 @@ dependencies = [
 
 [[package]]
 name = "casper-executor-wasm-common"
-version = "0.1.0"
+version = "0.1.2"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "blake2 0.10.6",
  "borsh",
- "casper-sdk-sys 0.1.0",
+ "casper-contract-sdk-sys",
  "hex",
  "num-derive",
  "num-traits",
@@ -901,28 +920,13 @@ dependencies = [
  "thiserror 2.0.12",
 ]
 
-[[package]]
-name = "casper-executor-wasm-common"
-version = "0.1.0"
-source = "git+https://github.com/casper-network/casper-node.git?branch=dev#0803b7a7492b03fc6f10e3821748498264fd3a98"
-dependencies = [
- "bitflags 2.9.0",
- "blake2 0.10.6",
- "borsh",
- "casper-sdk-sys 0.1.0 (git+https://github.com/casper-network/casper-node.git?branch=dev)",
- "num-derive",
- "num-traits",
- "serde",
- "thiserror 2.0.12",
-]
-
 [[package]]
 name = "casper-executor-wasm-host"
-version = "0.1.0"
+version = "0.1.2"
 dependencies = [
  "base16",
  "bytes",
- "casper-executor-wasm-common 0.1.0",
+ "casper-executor-wasm-common",
  "casper-executor-wasm-interface",
  "casper-storage",
  "casper-types",
@@ -937,11 +941,11 @@ dependencies = [
 
 [[package]]
 name = "casper-executor-wasm-interface"
-version = "0.1.0"
+version = "0.1.2"
 dependencies = [
  "borsh",
  "bytes",
- "casper-executor-wasm-common 0.1.0",
+ "casper-executor-wasm-common",
  "casper-storage",
  "casper-types",
  "parking_lot",
@@ -950,13 +954,13 @@ dependencies = [
 
 [[package]]
 name = "casper-executor-wasmer-backend"
-version = "0.1.0"
+version = "0.1.2"
 dependencies = [
  "bytes",
- "casper-executor-wasm-common 0.1.0",
+ "casper-contract-sdk-sys",
+ "casper-executor-wasm-common",
  "casper-executor-wasm-host",
  "casper-executor-wasm-interface",
- "casper-sdk-sys 0.1.0",
  "casper-storage",
  "casper-types",
  "regex",
@@ -968,40 +972,9 @@ dependencies = [
  "wat",
 ]
 
-[[package]]
-name = "casper-macros"
-version = "0.1.0"
-dependencies = [
- "blake2-rfc",
- "casper-executor-wasm-common 0.1.0",
- "casper-sdk-sys 0.1.0",
- "darling",
- "paste",
- "proc-macro2",
- "quote",
- "static_assertions",
- "syn 2.0.101",
-]
-
-[[package]]
-name = "casper-macros"
-version = "0.1.0"
-source = "git+https://github.com/casper-network/casper-node.git?branch=dev#0803b7a7492b03fc6f10e3821748498264fd3a98"
-dependencies = [
- "blake2-rfc",
- "casper-executor-wasm-common 0.1.0 (git+https://github.com/casper-network/casper-node.git?branch=dev)",
- "casper-sdk-sys 0.1.0 (git+https://github.com/casper-network/casper-node.git?branch=dev)",
- "darling",
- "paste",
- "proc-macro2",
- "quote",
- "static_assertions",
- "syn 2.0.101",
-]
-
 [[package]]
 name = "casper-node"
-version = "2.0.0"
+version = "2.1.0"
 dependencies = [
  "ansi_term",
  "anyhow",
@@ -1084,7 +1057,7 @@ dependencies = [
  "tokio-serde",
  "tokio-stream",
  "tokio-util 0.6.10",
- "toml 0.8.21",
+ "toml 0.8.22",
  "tower",
  "tracing",
  "tracing-futures",
@@ -1095,78 +1068,9 @@ dependencies = [
  "wheelbuf",
 ]
 
-[[package]]
-name = "casper-sdk"
-version = "0.1.0"
-dependencies = [
- "base16",
- "bitflags 2.9.0",
- "bnum",
- "borsh",
- "bytes",
- "casper-executor-wasm-common 0.1.0",
- "casper-macros 0.1.0",
- "casper-sdk-sys 0.1.0",
- "cfg-if 1.0.0",
- "clap 4.5.37",
- "const-fnv1a-hash",
- "impl-trait-for-tuples",
- "linkme",
- "once_cell",
- "rand",
- "serde",
- "serde_json",
- "thiserror 2.0.12",
-]
-
-[[package]]
-name = "casper-sdk"
-version = "0.1.0"
-source = "git+https://github.com/casper-network/casper-node.git?branch=dev#0803b7a7492b03fc6f10e3821748498264fd3a98"
-dependencies = [
- "bitflags 2.9.0",
- "borsh",
- "bytes",
- "casper-executor-wasm-common 0.1.0 (git+https://github.com/casper-network/casper-node.git?branch=dev)",
- "casper-macros 0.1.0 (git+https://github.com/casper-network/casper-node.git?branch=dev)",
- "casper-sdk-sys 0.1.0 (git+https://github.com/casper-network/casper-node.git?branch=dev)",
- "cfg-if 1.0.0",
- "const-fnv1a-hash",
- "impl-trait-for-tuples",
- "linkme",
- "once_cell",
- "rand",
- "serde",
- "serde_json",
-]
-
-[[package]]
-name = "casper-sdk-codegen"
-version = "0.1.0"
-dependencies = [
- "borsh",
- "casper-sdk 0.1.0",
- "codegen",
- "indexmap 2.9.0",
- "serde",
- "serde_json",
- "syn 2.0.101",
- "tempfile",
- "trybuild",
-]
-
-[[package]]
-name = "casper-sdk-sys"
-version = "0.1.0"
-
-[[package]]
-name = "casper-sdk-sys"
-version = "0.1.0"
-source = "git+https://github.com/casper-network/casper-node.git?branch=dev#0803b7a7492b03fc6f10e3821748498264fd3a98"
-
 [[package]]
 name = "casper-storage"
-version = "2.0.0"
+version = "2.1.0"
 dependencies = [
  "anyhow",
  "assert_matches",
@@ -1199,7 +1103,7 @@ dependencies = [
 
 [[package]]
 name = "casper-types"
-version = "5.0.1"
+version = "6.0.0"
 dependencies = [
  "base16",
  "base64 0.13.1",
@@ -1249,9 +1153,9 @@ dependencies = [
 
 [[package]]
 name = "casper-updater"
-version = "0.3.0"
+version = "0.4.0"
 dependencies = [
- "clap 4.5.37",
+ "clap 4.5.38",
  "once_cell",
  "regex",
  "semver",
@@ -1330,12 +1234,10 @@ checksum = "37b2a672a2cb129a2e41c10b1224bb368f9f37a2b16b612598138befd7b37eb5"
 
 [[package]]
 name = "cc"
-version = "1.2.20"
+version = "1.2.23"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "04da6a0d40b948dfc4fa8f5bbf402b0fc1a64a28dbf7d12ffd683550f2c1b63a"
+checksum = "5f4ac86a9e5bc1e2b3449ab9d7d3a6a405e3d1bb28d7b9be8614f55846ae3766"
 dependencies = [
- "jobserver",
- "libc",
  "shlex",
 ]
 
@@ -1401,16 +1303,6 @@ dependencies = [
  "half",
 ]
 
-[[package]]
-name = "cipher"
-version = "0.4.4"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "773f3b9af64447d2ce9850330c473515014aa235e6a783b02db81ff39e4a3dad"
-dependencies = [
- "crypto-common",
- "inout",
-]
-
 [[package]]
 name = "clang-sys"
 version = "1.8.1"
@@ -1456,9 +1348,9 @@ dependencies = [
 
 [[package]]
 name = "clap"
-version = "4.5.37"
+version = "4.5.38"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "eccb054f56cbd38340b380d4a8e69ef1f02f1af43db2f0cc817a4774d80ae071"
+checksum = "ed93b9805f8ba930df42c2590f05453d5ec36cbb85d018868a5b24d31f6ac000"
 dependencies = [
  "clap_builder",
  "clap_derive 4.5.32",
@@ -1472,14 +1364,14 @@ checksum = "23b2ea69cefa96b848b73ad516ad1d59a195cdf9263087d977f648a818c8b43e"
 dependencies = [
  "anstyle",
  "cargo_metadata 0.18.1",
- "clap 4.5.37",
+ "clap 4.5.38",
 ]
 
 [[package]]
 name = "clap_builder"
-version = "4.5.37"
+version = "4.5.38"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "efd9466fac8543255d3b1fcad4762c5e116ffe808c8a3043d4263cd4fd4862a2"
+checksum = "379026ff283facf611b0ea629334361c4211d1b12ee01024eec1591133b04120"
 dependencies = [
  "anstream",
  "anstyle",
@@ -1702,21 +1594,6 @@ dependencies = [
  "libc",
 ]
 
-[[package]]
-name = "crc"
-version = "3.2.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "69e6e4d7b33a94f0991c26729976b10ebde1d34c3ee82408fb536164fa10d636"
-dependencies = [
- "crc-catalog",
-]
-
-[[package]]
-name = "crc-catalog"
-version = "2.4.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "19d374276b40fb8bbdee95aef7c7fa6b5316ec764510eb64b8dd0e2ed0d7e7f5"
-
 [[package]]
 name = "crc32fast"
 version = "1.4.2"
@@ -1789,7 +1666,7 @@ dependencies = [
  "anes",
  "cast",
  "ciborium",
- "clap 4.5.37",
+ "clap 4.5.38",
  "criterion-plot",
  "is-terminal",
  "itertools 0.10.5",
@@ -1856,7 +1733,7 @@ version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d8b9f2e4c67f833b660cdb0a3523065869fb35570177239812ed4c905aeff87b"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "crossterm_winapi",
  "derive_more 2.0.1",
  "document-features",
@@ -2040,12 +1917,6 @@ dependencies = [
  "uuid 1.16.0",
 ]
 
-[[package]]
-name = "deflate64"
-version = "0.1.9"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "da692b8d1080ea3045efaab14434d40468c3d8657e42abddfffca87b428f4c1b"
-
 [[package]]
 name = "delegate"
 version = "0.1.0"
@@ -2064,26 +1935,6 @@ dependencies = [
  "zeroize",
 ]
 
-[[package]]
-name = "deranged"
-version = "0.4.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9c9e6a11ca8224451684bc0d7d5a7adbf8f2fd6887261a1cfc3c0432f9d4068e"
-dependencies = [
- "powerfmt",
-]
-
-[[package]]
-name = "derive_arbitrary"
-version = "1.4.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "30542c1ad912e0e3d22a1935c290e12e8a29d704a420177a31faad4a601a0800"
-dependencies = [
- "proc-macro2",
- "quote",
- "syn 2.0.101",
-]
-
 [[package]]
 name = "derive_more"
 version = "0.99.20"
@@ -2636,18 +2487,18 @@ dependencies = [
 
 [[package]]
 name = "enumset"
-version = "1.1.5"
+version = "1.1.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d07a4b049558765cef5f0c1a273c3fc57084d768b44d2f98127aef4cceb17293"
+checksum = "11a6b7c3d347de0a9f7bfd2f853be43fe32fa6fac30c70f6d6d67a1e936b87ee"
 dependencies = [
  "enumset_derive",
 ]
 
 [[package]]
 name = "enumset_derive"
-version = "0.10.0"
+version = "0.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "59c3b24c345d8c314966bdc1832f6c2635bfcce8e7cf363bd115987bba2ee242"
+checksum = "6da3ea9e1d1a3b1593e15781f930120e72aa7501610b2f82e5b6739c72e8eac5"
 dependencies = [
  "darling",
  "proc-macro2",
@@ -2705,9 +2556,9 @@ dependencies = [
 
 [[package]]
 name = "errno"
-version = "0.3.11"
+version = "0.3.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "976dd42dc7e85965fe702eb8164f21f450704bdde31faefd6471dba214cb594e"
+checksum = "cea14ef9355e3beab063703aa9dab15afd25f0667c341310c1e5274bb1d0da18"
 dependencies = [
  "libc",
  "windows-sys 0.59.0",
@@ -3079,16 +2930,14 @@ dependencies = [
 
 [[package]]
 name = "getrandom"
-version = "0.3.2"
+version = "0.3.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "73fea8450eea4bac3940448fb7ae50d91f034f941199fcd9d909a5a07aa455f0"
+checksum = "26145e563e54f2cadc477553f1ec5ee650b00862f0a58bcd12cbdc5f0ea2d2f4"
 dependencies = [
  "cfg-if 1.0.0",
- "js-sys",
  "libc",
  "r-efi",
  "wasi 0.14.2+wasi-0.2.4",
- "wasm-bindgen",
 ]
 
 [[package]]
@@ -3295,9 +3144,9 @@ dependencies = [
 
 [[package]]
 name = "hashbrown"
-version = "0.15.2"
+version = "0.15.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bf151400ff0baff5465007dd2f3e717f3fe502074ca563069ce3a6629d07b289"
+checksum = "84b26c544d002229e640969970a2e74021aadf6e2f96372b9c58eff97de08eb3"
 
 [[package]]
 name = "headers"
@@ -3369,9 +3218,9 @@ checksum = "d231dfb89cfffdbc30e7fc41579ed6066ad03abda9e567ccafae602b97ec5024"
 
 [[package]]
 name = "hermit-abi"
-version = "0.5.0"
+version = "0.5.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fbd780fe5cc30f81464441920d82ac8740e2e46b29a6fad543ddd075229ce37e"
+checksum = "f154ce46856750ed433c8649605bf7ed2de3bc35fd9d2a9f30cddd873c80cb08"
 
 [[package]]
 name = "hex"
@@ -3535,21 +3384,22 @@ dependencies = [
 
 [[package]]
 name = "icu_collections"
-version = "1.5.0"
+version = "2.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "db2fa452206ebee18c4b5c2274dbf1de17008e874b4dc4f0aea9d01ca79e4526"
+checksum = "200072f5d0e3614556f94a9930d5dc3e0662a652823904c3a75dc3b0af7fee47"
 dependencies = [
  "displaydoc",
+ "potential_utf",
  "yoke",
  "zerofrom",
  "zerovec",
 ]
 
 [[package]]
-name = "icu_locid"
-version = "1.5.0"
+name = "icu_locale_core"
+version = "2.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "13acbb8371917fc971be86fc8057c41a64b521c184808a698c02acc242dbf637"
+checksum = "0cde2700ccaed3872079a65fb1a78f6c0a36c91570f28755dda67bc8f7d9f00a"
 dependencies = [
  "displaydoc",
  "litemap",
@@ -3558,99 +3408,66 @@ dependencies = [
  "zerovec",
 ]
 
-[[package]]
-name = "icu_locid_transform"
-version = "1.5.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "01d11ac35de8e40fdeda00d9e1e9d92525f3f9d887cdd7aa81d727596788b54e"
-dependencies = [
- "displaydoc",
- "icu_locid",
- "icu_locid_transform_data",
- "icu_provider",
- "tinystr",
- "zerovec",
-]
-
-[[package]]
-name = "icu_locid_transform_data"
-version = "1.5.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7515e6d781098bf9f7205ab3fc7e9709d34554ae0b21ddbcb5febfa4bc7df11d"
-
 [[package]]
 name = "icu_normalizer"
-version = "1.5.0"
+version = "2.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "19ce3e0da2ec68599d193c93d088142efd7f9c5d6fc9b803774855747dc6a84f"
+checksum = "436880e8e18df4d7bbc06d58432329d6458cc84531f7ac5f024e93deadb37979"
 dependencies = [
  "displaydoc",
  "icu_collections",
  "icu_normalizer_data",
  "icu_properties",
  "icu_provider",
  "smallvec",
- "utf16_iter",
- "utf8_iter",
- "write16",
  "zerovec",
 ]
 
 [[package]]
 name = "icu_normalizer_data"
-version = "1.5.1"
+version = "2.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c5e8338228bdc8ab83303f16b797e177953730f601a96c25d10cb3ab0daa0cb7"
+checksum = "00210d6893afc98edb752b664b8890f0ef174c8adbb8d0be9710fa66fbbf72d3"
 
 [[package]]
 name = "icu_properties"
-version = "1.5.1"
+version = "2.0.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "93d6020766cfc6302c15dbbc9c8778c37e62c14427cb7f6e601d849e092aeef5"
+checksum = "016c619c1eeb94efb86809b015c58f479963de65bdb6253345c1a1276f22e32b"
 dependencies = [
  "displaydoc",
  "icu_collections",
- "icu_locid_transform",
+ "icu_locale_core",
  "icu_properties_data",
  "icu_provider",
- "tinystr",
+ "potential_utf",
+ "zerotrie",
  "zerovec",
 ]
 
 [[package]]
 name = "icu_properties_data"
-version = "1.5.1"
+version = "2.0.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "85fb8799753b75aee8d2a21d7c14d9f38921b54b3dbda10f5a3c7a7b82dba5e2"
+checksum = "298459143998310acd25ffe6810ed544932242d3f07083eee1084d83a71bd632"
 
 [[package]]
 name = "icu_provider"
-version = "1.5.0"
+version = "2.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6ed421c8a8ef78d3e2dbc98a973be2f3770cb42b606e3ab18d6237c4dfde68d9"
+checksum = "03c80da27b5f4187909049ee2d72f276f0d9f99a42c306bd0131ecfe04d8e5af"
 dependencies = [
  "displaydoc",
- "icu_locid",
- "icu_provider_macros",
+ "icu_locale_core",
  "stable_deref_trait",
  "tinystr",
  "writeable",
  "yoke",
  "zerofrom",
+ "zerotrie",
  "zerovec",
 ]
 
-[[package]]
-name = "icu_provider_macros"
-version = "1.5.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1ec89e9337638ecdc08744df490b221a7399bf8d164eb52a665454e60e075ad6"
-dependencies = [
- "proc-macro2",
- "quote",
- "syn 2.0.101",
-]
-
 [[package]]
 name = "id-arena"
 version = "2.2.1"
@@ -3676,9 +3493,9 @@ dependencies = [
 
 [[package]]
 name = "idna_adapter"
-version = "1.2.0"
+version = "1.2.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "daca1df1c957320b2cf139ac61e7bd64fed304c5040df000a745aa1de3b4ef71"
+checksum = "3acae9609540aa318d1bc588455225fb2085b9ed0c4f6bd0d9d5bcd86f1a0344"
 dependencies = [
  "icu_normalizer",
  "icu_properties",
@@ -3746,7 +3563,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cea70ddb795996207ad57735b50c5982d8844f38ba9ee5f1aedcfb708a2aa11e"
 dependencies = [
  "equivalent",
- "hashbrown 0.15.2",
+ "hashbrown 0.15.3",
 ]
 
 [[package]]
@@ -3767,15 +3584,6 @@ dependencies = [
  "str_stack",
 ]
 
-[[package]]
-name = "inout"
-version = "0.1.4"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "879f10e63c20629ecabbb64a8010319738c66a5cd0c29b02d63d272b03751d01"
-dependencies = [
- "generic-array",
-]
-
 [[package]]
 name = "ipnet"
 version = "2.11.0"
@@ -3797,7 +3605,7 @@ version = "0.4.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e04d7f318608d35d4b61ddd75cbdaee86b023ebe2bd5a66ee0915f0bf93095a9"
 dependencies = [
- "hermit-abi 0.5.0",
+ "hermit-abi 0.5.1",
  "libc",
  "windows-sys 0.59.0",
 ]
@@ -3850,16 +3658,6 @@ version = "1.0.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4a5f13b858c8d314ee3e8f639011f7ccefe71f97f96e50151fb991f267928e2c"
 
-[[package]]
-name = "jobserver"
-version = "0.1.33"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "38f262f097c174adebe41eb73d66ae9c06b2844fb0da69969647bbddd9b0538a"
-dependencies = [
- "getrandom 0.3.2",
- "libc",
-]
-
 [[package]]
 name = "js-sys"
 version = "0.3.77"
@@ -3916,27 +3714,27 @@ checksum = "d750af042f7ef4f724306de029d18836c26c1765a54a6a3f094cbd23a7267ffa"
 
 [[package]]
 name = "libloading"
-version = "0.8.6"
+version = "0.8.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fc2f4eb4bc735547cfed7c0a4922cbd04a4655978c09b54f1f7b228750664c34"
+checksum = "6a793df0d7afeac54f95b471d3af7f0d4fb975699f972341a4b76988d49cdf0c"
 dependencies = [
  "cfg-if 1.0.0",
- "windows-targets 0.52.6",
+ "windows-targets 0.53.0",
 ]
 
 [[package]]
 name = "libm"
-version = "0.2.13"
+version = "0.2.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c9627da5196e5d8ed0b0495e61e518847578da83483c37288316d9b2e03a7f72"
+checksum = "f9fbbcab51052fe104eb5e5d351cf728d30a5be1fe14d9be8a3b097481fb97de"
 
 [[package]]
 name = "libredox"
 version = "0.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c0ff37bd590ca25063e35af745c343cb7a0271906fb7b37e4813e8f79f00268d"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "libc",
  "redox_syscall",
 ]
@@ -3991,9 +3789,9 @@ dependencies = [
 
 [[package]]
 name = "litemap"
-version = "0.7.5"
+version = "0.8.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "23fb14cb19457329c82206317a5663005a4d404783dc74f4252769b0d5f42856"
+checksum = "241eaef5fd12c88705a01fc1066c48c4b36e0dd4377dcdc7ec3942cea7a69956"
 
 [[package]]
 name = "litrs"
@@ -4052,27 +3850,6 @@ dependencies = [
  "value-bag",
 ]
 
-[[package]]
-name = "lzma-rs"
-version = "0.3.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "297e814c836ae64db86b36cf2a557ba54368d03f6afcd7d947c266692f71115e"
-dependencies = [
- "byteorder",
- "crc",
-]
-
-[[package]]
-name = "lzma-sys"
-version = "0.1.20"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5fda04ab3764e6cde78b9974eec4f779acaba7c4e84b36eca3cf77c581b85d27"
-dependencies = [
- "cc",
- "libc",
- "pkg-config",
-]
-
 [[package]]
 name = "mach"
 version = "0.3.2"
@@ -4451,12 +4228,6 @@ dependencies = [
  "num-traits",
 ]
 
-[[package]]
-name = "num-conv"
-version = "0.1.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "51d515d32fb182ee37cda2ccdcb92950d6a3c2893aa280e540671c2cd0f3b1d9"
-
 [[package]]
 name = "num-derive"
 version = "0.4.2"
@@ -4576,7 +4347,7 @@ version = "0.10.72"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fedfea7d58a1f73118430a55da6a286e7b044961736ce96a16a17068ea25e5da"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "cfg-if 1.0.0",
  "foreign-types",
  "libc",
@@ -4613,9 +4384,9 @@ dependencies = [
 
 [[package]]
 name = "openssl-sys"
-version = "0.9.107"
+version = "0.9.108"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8288979acd84749c744a9014b4382d42b8f7b2592847b5afb2ed29e5d16ede07"
+checksum = "e145e1651e858e820e4860f7b9c5e169bc1d8ce1c86043be79fa7b7634821847"
 dependencies = [
  "cc",
  "libc",
@@ -4698,16 +4469,6 @@ dependencies = [
  "casper-types",
 ]
 
-[[package]]
-name = "pbkdf2"
-version = "0.12.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f8ed6a7761f76e3b9f92dfb0a60a6a6477c61024b775147ff0973a02653abaf2"
-dependencies = [
- "digest 0.10.7",
- "hmac",
-]
-
 [[package]]
 name = "pem"
 version = "0.8.3"
@@ -4890,10 +4651,13 @@ dependencies = [
 ]
 
 [[package]]
-name = "powerfmt"
-version = "0.2.0"
+name = "potential_utf"
+version = "0.1.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "439ee305def115ba05938db6eb1644ff94165c5ab5e9420d1c1bcedbba909391"
+checksum = "e5a7c30837279ca13e7c867e9e40053bc68740f988cb07f7ca6df43cc734b585"
+dependencies = [
+ "zerovec",
+]
 
 [[package]]
 name = "pprof"
@@ -4924,7 +4688,7 @@ version = "0.2.21"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "85eae3c4ed2f50dcfe72643da4befc30deadb458a9b590d720cde2f2b1e97da9"
 dependencies = [
- "zerocopy 0.8.25",
+ "zerocopy",
 ]
 
 [[package]]
@@ -4955,7 +4719,7 @@ version = "3.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "edce586971a4dfaa28950c6f18ed55e0406c1ab88bbce2c6f6293a7aaba73d35"
 dependencies = [
- "toml_edit 0.22.25",
+ "toml_edit 0.22.26",
 ]
 
 [[package]]
@@ -5013,14 +4777,6 @@ dependencies = [
  "unicode-ident",
 ]
 
-[[package]]
-name = "project-template"
-version = "0.1.0"
-dependencies = [
- "casper-macros 0.1.0 (git+https://github.com/casper-network/casper-node.git?branch=dev)",
- "casper-sdk 0.1.0 (git+https://github.com/casper-network/casper-node.git?branch=dev)",
-]
-
 [[package]]
 name = "prometheus"
 version = "0.13.4"
@@ -5043,7 +4799,7 @@ checksum = "14cae93065090804185d3b75f0bf93b8eeda30c7a9b4a33d3bdb3988d6229e50"
 dependencies = [
  "bit-set",
  "bit-vec",
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "lazy_static",
  "num-traits",
  "rand",
@@ -5123,7 +4879,7 @@ version = "0.9.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "57206b407293d2bcd3af849ce869d52068623f19e1b5ff8e8778e3309439682b"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "memchr",
  "unicase",
 ]
@@ -5326,11 +5082,11 @@ dependencies = [
 
 [[package]]
 name = "redox_syscall"
-version = "0.5.11"
+version = "0.5.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d2f103c6d277498fbceb16e84d317e2a400f160f46904d5f5410848c829511a3"
+checksum = "928fca9cf2aa042393a8325b9ead81d2f0df4cb12e1e24cef072922ccd99c5af"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
 ]
 
 [[package]]
@@ -5649,7 +5405,7 @@ checksum = "1e147371c75553e1e2fcdb483944a8540b8438c31426279553b9a8182a9b7b65"
 dependencies = [
  "bytecheck 0.8.1",
  "bytes",
- "hashbrown 0.15.2",
+ "hashbrown 0.15.3",
  "indexmap 2.9.0",
  "munge",
  "ptr_meta 0.3.0",
@@ -5716,11 +5472,11 @@ dependencies = [
 
 [[package]]
 name = "rustix"
-version = "1.0.5"
+version = "1.0.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d97817398dd4bb2e6da002002db259209759911da105da92bec29ccb12cf58bf"
+checksum = "c71e83d6afe7ff64890ec6b71d6a69bb8a610ab78ce364b3352876bb4c801266"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "errno",
  "libc",
  "linux-raw-sys",
@@ -5729,9 +5485,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.26"
+version = "0.23.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "df51b5869f3a441595eac5e8ff14d486ff285f7b8c0df8770e49c3b56351f0f0"
+checksum = "730944ca083c1c233a75c09f199e973ca499344a2b7ba9e755c457e86fb4a321"
 dependencies = [
  "log",
  "once_cell",
@@ -5753,15 +5509,18 @@ dependencies = [
 
 [[package]]
 name = "rustls-pki-types"
-version = "1.11.0"
+version = "1.12.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "917ce264624a4b4db1c364dcc35bfca9ded014d0a958cd47ad3e960e988ea51c"
+checksum = "229a4a4c221013e7e1f1a043678c5cc39fe5171437c88fb47151a21e6f5b5c79"
+dependencies = [
+ "zeroize",
+]
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.1"
+version = "0.103.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fef8b8769aaccf73098557a87cd1816b4f9c7c16811c9c77142aa695c16f2c03"
+checksum = "e4a72fe2bcf7a6ac6fd7d0b9e5cb68aeb7d4c0a0271730218b3e92d43b4eb435"
 dependencies = [
  "ring",
  "rustls-pki-types",
@@ -5883,7 +5642,7 @@ version = "2.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "897b2245f0b511c87893af39b033e5ca9cce68824c4d7e7630b5a1d339658d02"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "core-foundation",
  "core-foundation-sys",
  "libc",
@@ -6060,9 +5819,9 @@ dependencies = [
 
 [[package]]
 name = "sha2"
-version = "0.10.8"
+version = "0.10.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "793db75ad2bcafc3ffa7c68b215fee268f537982cd901d132f89c6343f3a3dc8"
+checksum = "a7507d819769d01a365ab707794a4084392c824f54a7a6a7862f8c3d0892b283"
 dependencies = [
  "cfg-if 1.0.0",
  "cpufeatures",
@@ -6096,9 +5855,9 @@ checksum = "0fda2ff0d084019ba4d7c6f371c95d8fd75ce3524c3cb8fb653a3023f6323e64"
 
 [[package]]
 name = "signal-hook"
-version = "0.3.17"
+version = "0.3.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8621587d4798caf8eb44879d42e56b9a93ea5dcd315a6487c357130095b62801"
+checksum = "d881a16cf4426aa584979d30bd82cb33429027e42122b169753d6ef1085ed6e2"
 dependencies = [
  "libc",
  "signal-hook-registry",
@@ -6140,12 +5899,6 @@ dependencies = [
  "rand_core",
 ]
 
-[[package]]
-name = "simd-adler32"
-version = "0.3.7"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d66dc143e6b11c1eddc06d5c423cfc97062865baf299914ab64caa38182078fe"
-
 [[package]]
 name = "simdutf8"
 version = "0.1.5"
@@ -6347,9 +6100,9 @@ checksum = "13c2bddecc57b384dee18652358fb23172facb8a2c51ccc10d74c157bdea3292"
 
 [[package]]
 name = "symbolic-common"
-version = "12.15.4"
+version = "12.15.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "23eae23242dffa2e8e66c0e20f4ca1e28391f64e361db1e921a209c9bc70ec3a"
+checksum = "6a1150bdda9314f6cfeeea801c23f5593c6e6a6c72e64f67e48d723a12b8efdb"
 dependencies = [
  "debugid",
  "memmap2 0.9.5",
@@ -6359,9 +6112,9 @@ dependencies = [
 
 [[package]]
 name = "symbolic-demangle"
-version = "12.15.4"
+version = "12.15.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "153faacda0d58dc1eb3e8bbd5dab998041e95bd7f4ab2caeeadc89410617f144"
+checksum = "9f66537def48fbc704a92e4fdaab7833bc7cb2255faca8182592fb5fa617eb82"
 dependencies = [
  "cpp_demangle",
  "rustc-demangle",
@@ -6398,9 +6151,9 @@ checksum = "2047c6ded9c721764247e62cd3b03c09ffc529b2ba5b10ec482ae507a4a70160"
 
 [[package]]
 name = "synstructure"
-version = "0.13.1"
+version = "0.13.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c8af7666ab7b6390ab78131fb5b0fce11d6b7a6951602017c35fa82800708971"
+checksum = "728a70f3dbaf5bab7f0c4b1ac8d7ae5ea60a4b5549c8a5914361c99147a709d2"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -6471,12 +6224,12 @@ checksum = "1ac9aa371f599d22256307c24a9d748c041e548cbf599f35d890f9d365361790"
 
 [[package]]
 name = "tempfile"
-version = "3.19.1"
+version = "3.20.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7437ac7763b9b123ccf33c338a5cc1bac6f69b45a136c19bdd8a65e3916435bf"
+checksum = "e8a64e3985349f2441a1a9ef0b853f869006c3855f2cda6862a94d26ebb9d6a1"
 dependencies = [
  "fastrand",
- "getrandom 0.3.2",
+ "getrandom 0.3.3",
  "once_cell",
  "rustix",
  "windows-sys 0.59.0",
@@ -6574,30 +6327,11 @@ dependencies = [
  "once_cell",
 ]
 
-[[package]]
-name = "time"
-version = "0.3.41"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8a7619e19bc266e0f9c5e6686659d394bc57973859340060a69221e57dbc0c40"
-dependencies = [
- "deranged",
- "num-conv",
- "powerfmt",
- "serde",
- "time-core",
-]
-
-[[package]]
-name = "time-core"
-version = "0.1.4"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c9e9a38711f559d9e3ce1cdb06dd7c5b8ea546bc90052da6d06bb76da74bb07c"
-
 [[package]]
 name = "tinystr"
-version = "0.7.6"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9117f5d4db391c1cf6927e7bea3db74b9a1c1add8f7eda9ffd5364f40f57b82f"
+checksum = "5d4f6d1145dcb577acf783d4e601bc1d76a13337bb54e6233add580b07344c8b"
 dependencies = [
  "displaydoc",
  "zerovec",
@@ -6630,9 +6364,9 @@ checksum = "1f3ccbac311fea05f86f61904b462b55fb3df8837a366dfc601a0161d0532f20"
 
 [[package]]
 name = "tokio"
-version = "1.44.2"
+version = "1.45.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e6b88822cbe49de4185e3a4cbf8321dd487cf5fe0c5c65695fef6346371e9c48"
+checksum = "2513ca694ef9ede0fb23fe71a4ee4107cb102b9dc1930f6d0fd77aae068ae165"
 dependencies = [
  "backtrace",
  "bytes",
@@ -6765,15 +6499,15 @@ dependencies = [
 
 [[package]]
 name = "toml"
-version = "0.8.21"
+version = "0.8.22"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "900f6c86a685850b1bc9f6223b20125115ee3f31e01207d81655bbcc0aea9231"
+checksum = "05ae329d1f08c4d17a59bed7ff5b5a769d062e64a62d34a3261b219e62cd5aae"
 dependencies = [
  "indexmap 2.9.0",
  "serde",
  "serde_spanned",
  "toml_datetime",
- "toml_edit 0.22.25",
+ "toml_edit 0.22.26",
 ]
 
 [[package]]
@@ -6811,23 +6545,23 @@ dependencies = [
 
 [[package]]
 name = "toml_edit"
-version = "0.22.25"
+version = "0.22.26"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "10558ed0bd2a1562e630926a2d1f0b98c827da99fabd3fe20920a59642504485"
+checksum = "310068873db2c5b3e7659d2cc35d21855dbafa50d1ce336397c666e3cb08137e"
 dependencies = [
  "indexmap 2.9.0",
  "serde",
  "serde_spanned",
  "toml_datetime",
  "toml_write",
- "winnow 0.7.7",
+ "winnow 0.7.10",
 ]
 
 [[package]]
 name = "toml_write"
-version = "0.1.0"
+version = "0.1.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "28391a4201ba7eb1984cfeb6862c0b3ea2cfe23332298967c749dddc0d6cd976"
+checksum = "bfb942dfe1d8e29a7ee7fcbde5bd2b9a25fb89aa70caea2eba3bee836ff41076"
 
 [[package]]
 name = "tower"
@@ -7079,17 +6813,17 @@ checksum = "e421abadd41a4225275504ea4d6566923418b7f05506fbc9c0fe86ba7396114b"
 
 [[package]]
 name = "trybuild"
-version = "1.0.104"
+version = "1.0.105"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6ae08be68c056db96f0e6c6dd820727cca756ced9e1f4cc7fdd20e2a55e23898"
+checksum = "1c9bf9513a2f4aeef5fdac8677d7d349c79fdbcc03b9c86da6e9d254f1e43be2"
 dependencies = [
  "glob 0.3.2",
  "serde",
  "serde_derive",
  "serde_json",
  "target-triple",
  "termcolor",
- "toml 0.8.21",
+ "toml 0.8.22",
 ]
 
 [[package]]
@@ -7117,7 +6851,7 @@ version = "1.6.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "97fee6b57c6a41524a810daee9286c02d7752c4253064d0b05472833a438f675"
 dependencies = [
- "cfg-if 1.0.0",
+ "cfg-if 0.1.10",
  "static_assertions",
 ]
 
@@ -7232,7 +6966,7 @@ dependencies = [
  "rustls",
  "rustls-pki-types",
  "url",
- "webpki-roots",
+ "webpki-roots 0.26.11",
 ]
 
 [[package]]
@@ -7252,12 +6986,6 @@ version = "0.7.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "09cc8ee72d2a9becf2f2febe0205bbed8fc6615b7cb429ad062dc7b7ddd036a9"
 
-[[package]]
-name = "utf16_iter"
-version = "1.0.5"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c8232dd3cdaed5356e0f716d285e4b40b932ac434100fe9b7e0e8e935b9e6246"
-
 [[package]]
 name = "utf8_iter"
 version = "1.0.4"
@@ -7343,8 +7071,8 @@ checksum = "0b928f33d975fc6ad9f86c8f283853ad26bdd5b10b7f1542aa2fa15e2289105a"
 name = "vm2-cep18"
 version = "0.1.0"
 dependencies = [
- "casper-sdk 0.1.0",
- "casper-sdk-codegen",
+ "casper-contract-sdk",
+ "casper-contract-sdk-codegen",
  "serde_json",
 ]
 
@@ -7353,24 +7081,24 @@ name = "vm2-cep18-caller"
 version = "0.1.0"
 dependencies = [
  "borsh",
- "casper-sdk 0.1.0",
+ "casper-contract-sdk",
  "vm2-cep18",
 ]
 
 [[package]]
 name = "vm2-flipper"
 version = "0.1.0"
 dependencies = [
- "casper-sdk 0.1.0",
+ "casper-contract-sdk",
 ]
 
 [[package]]
 name = "vm2-harness"
 version = "0.1.0"
 dependencies = [
- "casper-executor-wasm-common 0.1.0",
- "casper-macros 0.1.0",
- "casper-sdk 0.1.0",
+ "casper-contract-macros",
+ "casper-contract-sdk",
+ "casper-executor-wasm-common",
  "impls",
  "serde_json",
  "thiserror 2.0.12",
@@ -7380,17 +7108,17 @@ dependencies = [
 name = "vm2-host"
 version = "0.1.0"
 dependencies = [
- "casper-macros 0.1.0",
- "casper-sdk 0.1.0",
+ "casper-contract-macros",
+ "casper-contract-sdk",
 ]
 
 [[package]]
 name = "vm2-legacy-counter-proxy"
 version = "0.1.0"
 dependencies = [
- "casper-macros 0.1.0",
- "casper-sdk 0.1.0",
- "casper-sdk-codegen",
+ "casper-contract-macros",
+ "casper-contract-sdk",
+ "casper-contract-sdk-codegen",
  "serde_json",
 ]
 
@@ -7399,25 +7127,25 @@ name = "vm2-trait"
 version = "0.1.0"
 dependencies = [
  "base16",
- "casper-macros 0.1.0",
- "casper-sdk 0.1.0",
+ "casper-contract-macros",
+ "casper-contract-sdk",
  "serde_json",
 ]
 
 [[package]]
 name = "vm2-upgradable"
 version = "0.1.0"
 dependencies = [
- "casper-macros 0.1.0",
- "casper-sdk 0.1.0",
+ "casper-contract-macros",
+ "casper-contract-sdk",
 ]
 
 [[package]]
 name = "vm2-upgradable-v2"
 version = "0.1.0"
 dependencies = [
- "casper-macros 0.1.0",
- "casper-sdk 0.1.0",
+ "casper-contract-macros",
+ "casper-contract-sdk",
 ]
 
 [[package]]
@@ -7632,12 +7360,12 @@ dependencies = [
 
 [[package]]
 name = "wasm-encoder"
-version = "0.229.0"
+version = "0.230.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "38ba1d491ecacb085a2552025c10a675a6fddcbd03b1fc9b36c536010ce265d2"
+checksum = "d4349d0943718e6e434b51b9639e876293093dca4b96384fb136ab5bd5ce6660"
 dependencies = [
  "leb128fmt",
- "wasmparser 0.229.0",
+ "wasmparser 0.230.0",
 ]
 
 [[package]]
@@ -7655,15 +7383,15 @@ dependencies = [
 
 [[package]]
 name = "wasmer"
-version = "5.0.4"
+version = "5.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "998dea47d6bb6a8fc7dd8a17b13bf8de277e007229f270c67105cb67fc2d9657"
+checksum = "8b104b9437e9100943fb01880cc210ebe250cc4aa2f7e121f068033a76d29cc4"
 dependencies = [
  "bindgen",
  "bytes",
  "cfg-if 1.0.0",
  "cmake",
- "indexmap 1.9.3",
+ "indexmap 2.9.0",
  "js-sys",
  "more-asserts",
  "rustc-demangle",
@@ -7682,22 +7410,19 @@ dependencies = [
  "wasmer-types",
  "wasmer-vm",
  "windows-sys 0.59.0",
- "xz",
- "zip",
 ]
 
 [[package]]
 name = "wasmer-compiler"
-version = "5.0.4"
+version = "5.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "082f48ba006cce2358f6c63d8dba732c9d12ba5833008c9ff2944290eb72c3dc"
+checksum = "d9dd5c640b9e6dcc64bcad987b3133e19f1c9919a8e0c732eb11a33f650bbf54"
 dependencies = [
  "backtrace",
  "bytes",
  "cfg-if 1.0.0",
  "enum-iterator 0.7.0",
  "enumset",
- "lazy_static",
  "leb128",
  "libc",
  "memmap2 0.6.2",
@@ -7719,16 +7444,15 @@ dependencies = [
 
 [[package]]
 name = "wasmer-compiler-singlepass"
-version = "5.0.4"
+version = "5.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "42d957e6c86cbae144823b707bf16eb62fc14c6867bf01cfd4fa9f5fef61f90b"
+checksum = "b95cad6ba04afeb3a339529e880c3290f8516bc6324c3082155a79f00129f5a1"
 dependencies = [
  "byteorder",
  "dynasm",
  "dynasmrt",
  "enumset",
  "gimli 0.28.1",
- "lazy_static",
  "more-asserts",
  "rayon",
  "smallvec",
@@ -7738,9 +7462,9 @@ dependencies = [
 
 [[package]]
 name = "wasmer-derive"
-version = "5.0.4"
+version = "5.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "87b16fa0b2199083143705698ea9fc2ffd0328d7061f54e0e20ccd0ec2020466"
+checksum = "1b4c4970530327054e6effa876eadfd57079866c7429e31fde2568d6354ec61d"
 dependencies = [
  "proc-macro-error2",
  "proc-macro2",
@@ -7750,9 +7474,9 @@ dependencies = [
 
 [[package]]
 name = "wasmer-middlewares"
-version = "5.0.4"
+version = "5.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "371b38abbba1a0fb747bee025d3a40c776842be4a2052b7a3ca18bd2db80669d"
+checksum = "111eee5478867554d4496f89f472499fe90469f7473dbf90e466c1deb5505293"
 dependencies = [
  "wasmer",
  "wasmer-types",
@@ -7761,9 +7485,9 @@ dependencies = [
 
 [[package]]
 name = "wasmer-types"
-version = "5.0.4"
+version = "5.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "41b0b9b3242c1a6269e544401b1741a56502a5f79db8e1b318cacf1b34b2690d"
+checksum = "554f389473d61915754b1873c5ef392a1a75b55c7d616e2a78f67c1af45785ae"
 dependencies = [
  "bytecheck 0.6.12",
  "enum-iterator 0.7.0",
@@ -7781,9 +7505,9 @@ dependencies = [
 
 [[package]]
 name = "wasmer-vm"
-version = "5.0.4"
+version = "5.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "92c7f8dbaceb0ab7901702e3c2bb43b09d2635aaa5ad39679c6560bcb9acde7c"
+checksum = "20b3f40e1e18d6cd040d6d1ea32affbf2f64ff059eff3b85614bccb8ff95c59b"
 dependencies = [
  "backtrace",
  "cc",
@@ -7794,7 +7518,6 @@ dependencies = [
  "enum-iterator 0.7.0",
  "fnv",
  "indexmap 2.9.0",
- "lazy_static",
  "libc",
  "mach2",
  "memoffset",
@@ -7819,7 +7542,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1cc7c63191ae61c70befbe6045b9be65ef2082fa89421a386ae172cb1e08e92d"
 dependencies = [
  "ahash",
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "hashbrown 0.14.5",
  "indexmap 2.9.0",
  "semver",
@@ -7831,17 +7554,17 @@ version = "0.219.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5220ee4c6ffcc0cb9d7c47398052203bc902c8ef3985b0c8134118440c0b2921"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "indexmap 2.9.0",
 ]
 
 [[package]]
 name = "wasmparser"
-version = "0.229.0"
+version = "0.230.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0cc3b1f053f5d41aa55640a1fa9b6d1b8a9e4418d118ce308d20e24ff3575a8c"
+checksum = "808198a69b5a0535583370a51d459baa14261dfab04800c4864ee9e1a14346ed"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
  "indexmap 2.9.0",
  "semver",
 ]
@@ -7859,22 +7582,22 @@ dependencies = [
 
 [[package]]
 name = "wast"
-version = "229.0.0"
+version = "230.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "63fcaff613c12225696bb163f79ca38ffb40e9300eff0ff4b8aa8b2f7eadf0d9"
+checksum = "b8edac03c5fa691551531533928443faf3dc61a44f814a235c7ec5d17b7b34f1"
 dependencies = [
  "bumpalo",
  "leb128fmt",
  "memchr",
  "unicode-width 0.2.0",
- "wasm-encoder 0.229.0",
+ "wasm-encoder 0.230.0",
 ]
 
 [[package]]
 name = "wat"
-version = "1.229.0"
+version = "1.230.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4189bad08b70455a9e9e67dc126d2dcf91fac143a80f1046747a5dde6d4c33e0"
+checksum = "0d77d62229e38db83eac32bacb5f61ebb952366ab0dae90cf2b3c07a65eea894"
 dependencies = [
  "wast",
 ]
@@ -7891,9 +7614,18 @@ dependencies = [
 
 [[package]]
 name = "webpki-roots"
-version = "0.26.9"
+version = "0.26.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "29aad86cec885cafd03e8305fd727c418e970a521322c91688414d5b8efba16b"
+checksum = "521bc38abb08001b01866da9f51eb7c5d647a19260e00054a8c7fd5f9e57f7a9"
+dependencies = [
+ "webpki-roots 1.0.0",
+]
+
+[[package]]
+name = "webpki-roots"
+version = "1.0.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "2853738d1cc4f2da3a225c18ec6c3721abb31961096e9dbf5ab35fa88b19cfdb"
 dependencies = [
  "rustls-pki-types",
 ]
@@ -7998,13 +7730,29 @@ dependencies = [
  "windows_aarch64_gnullvm 0.52.6",
  "windows_aarch64_msvc 0.52.6",
  "windows_i686_gnu 0.52.6",
- "windows_i686_gnullvm",
+ "windows_i686_gnullvm 0.52.6",
  "windows_i686_msvc 0.52.6",
  "windows_x86_64_gnu 0.52.6",
  "windows_x86_64_gnullvm 0.52.6",
  "windows_x86_64_msvc 0.52.6",
 ]
 
+[[package]]
+name = "windows-targets"
+version = "0.53.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "b1e4c7e8ceaaf9cb7d7507c974735728ab453b67ef8f18febdd7c11fe59dca8b"
+dependencies = [
+ "windows_aarch64_gnullvm 0.53.0",
+ "windows_aarch64_msvc 0.53.0",
+ "windows_i686_gnu 0.53.0",
+ "windows_i686_gnullvm 0.53.0",
+ "windows_i686_msvc 0.53.0",
+ "windows_x86_64_gnu 0.53.0",
+ "windows_x86_64_gnullvm 0.53.0",
+ "windows_x86_64_msvc 0.53.0",
+]
+
 [[package]]
 name = "windows_aarch64_gnullvm"
 version = "0.48.5"
@@ -8017,6 +7765,12 @@ version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "32a4622180e7a0ec044bb555404c800bc9fd9ec262ec147edd5989ccd0c02cd3"
 
+[[package]]
+name = "windows_aarch64_gnullvm"
+version = "0.53.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "86b8d5f90ddd19cb4a147a5fa63ca848db3df085e25fee3cc10b39b6eebae764"
+
 [[package]]
 name = "windows_aarch64_msvc"
 version = "0.48.5"
@@ -8029,6 +7783,12 @@ version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "09ec2a7bb152e2252b53fa7803150007879548bc709c039df7627cabbd05d469"
 
+[[package]]
+name = "windows_aarch64_msvc"
+version = "0.53.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c7651a1f62a11b8cbd5e0d42526e55f2c99886c77e007179efff86c2b137e66c"
+
 [[package]]
 name = "windows_i686_gnu"
 version = "0.48.5"
@@ -8041,12 +7801,24 @@ version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8e9b5ad5ab802e97eb8e295ac6720e509ee4c243f69d781394014ebfe8bbfa0b"
 
+[[package]]
+name = "windows_i686_gnu"
+version = "0.53.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c1dc67659d35f387f5f6c479dc4e28f1d4bb90ddd1a5d3da2e5d97b42d6272c3"
+
 [[package]]
 name = "windows_i686_gnullvm"
 version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0eee52d38c090b3caa76c563b86c3a4bd71ef1a819287c19d586d7334ae8ed66"
 
+[[package]]
+name = "windows_i686_gnullvm"
+version = "0.53.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9ce6ccbdedbf6d6354471319e781c0dfef054c81fbc7cf83f338a4296c0cae11"
+
 [[package]]
 name = "windows_i686_msvc"
 version = "0.48.5"
@@ -8059,6 +7831,12 @@ version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "240948bc05c5e7c6dabba28bf89d89ffce3e303022809e73deaefe4f6ec56c66"
 
+[[package]]
+name = "windows_i686_msvc"
+version = "0.53.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "581fee95406bb13382d2f65cd4a908ca7b1e4c2f1917f143ba16efe98a589b5d"
+
 [[package]]
 name = "windows_x86_64_gnu"
 version = "0.48.5"
@@ -8071,6 +7849,12 @@ version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "147a5c80aabfbf0c7d901cb5895d1de30ef2907eb21fbbab29ca94c5b08b1a78"
 
+[[package]]
+name = "windows_x86_64_gnu"
+version = "0.53.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "2e55b5ac9ea33f2fc1716d1742db15574fd6fc8dadc51caab1c16a3d3b4190ba"
+
 [[package]]
 name = "windows_x86_64_gnullvm"
 version = "0.48.5"
@@ -8083,6 +7867,12 @@ version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "24d5b23dc417412679681396f2b49f3de8c1473deb516bd34410872eff51ed0d"
 
+[[package]]
+name = "windows_x86_64_gnullvm"
+version = "0.53.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "0a6e035dd0599267ce1ee132e51c27dd29437f63325753051e71dd9e42406c57"
+
 [[package]]
 name = "windows_x86_64_msvc"
 version = "0.48.5"
@@ -8095,6 +7885,12 @@ version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "589f6da84c646204747d1270a2a5661ea66ed1cced2631d546fdfb155959f9ec"
 
+[[package]]
+name = "windows_x86_64_msvc"
+version = "0.53.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "271414315aff87387382ec3d271b52d7ae78726f5d44ac98b4f4030c91880486"
+
 [[package]]
 name = "winnow"
 version = "0.5.40"
@@ -8106,9 +7902,9 @@ dependencies = [
 
 [[package]]
 name = "winnow"
-version = "0.7.7"
+version = "0.7.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6cb8234a863ea0e8cd7284fcdd4f145233eb00fee02bbdd9861aec44e6477bc5"
+checksum = "c06928c8748d81b05c9be96aad92e1b6ff01833332f281e8cfca3be4b35fc9ec"
 dependencies = [
  "memchr",
 ]
@@ -8129,7 +7925,7 @@ version = "0.39.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6f42320e61fe2cfd34354ecb597f86f413484a798ba44a8ca1165c58d42da6c1"
 dependencies = [
- "bitflags 2.9.0",
+ "bitflags 2.9.1",
 ]
 
 [[package]]
@@ -8140,17 +7936,11 @@ dependencies = [
  "casper-types",
 ]
 
-[[package]]
-name = "write16"
-version = "1.0.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d1890f4022759daae28ed4fe62859b1236caebfc61ede2f63ed4e695f3f6d936"
-
 [[package]]
 name = "writeable"
-version = "0.5.5"
+version = "0.6.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1e9df38ee2d2c3c5948ea468a8406ff0db0b29ae1ffde1bcf20ef305bcc95c51"
+checksum = "ea2f10b9bb0928dfb1b42b65e1f9e36f7f54dbdf08457afefb38afcdec4fa2bb"
 
 [[package]]
 name = "xattr"
@@ -8168,29 +7958,11 @@ version = "0.8.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fdd20c5420375476fbd4394763288da7eb0cc0b8c11deed431a91562af7335d3"
 
-[[package]]
-name = "xz"
-version = "0.1.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3c887690ff2a2e233e8e49633461521f98ec57fbff9d59a884c9a4f04ec1da34"
-dependencies = [
- "xz2",
-]
-
-[[package]]
-name = "xz2"
-version = "0.1.7"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "388c44dc09d76f1536602ead6d325eb532f5c122f17782bd57fb47baeeb767e2"
-dependencies = [
- "lzma-sys",
-]
-
 [[package]]
 name = "yoke"
-version = "0.7.5"
+version = "0.8.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "120e6aef9aa629e3d4f52dc8cc43a015c7724194c97dfaf45180d2daf2b77f40"
+checksum = "5f41bb01b8226ef4bfd589436a297c53d118f65921786300e427be8d487695cc"
 dependencies = [
  "serde",
  "stable_deref_trait",
@@ -8200,43 +7972,23 @@ dependencies = [
 
 [[package]]
 name = "yoke-derive"
-version = "0.7.5"
+version = "0.8.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2380878cad4ac9aac1e2435f3eb4020e8374b5f13c296cb75b4620ff8e229154"
+checksum = "38da3c9736e16c5d3c8c597a9aaa5d1fa565d0532ae05e27c24aa62fb32c0ab6"
 dependencies = [
  "proc-macro2",
  "quote",
  "syn 2.0.101",
  "synstructure",
 ]
 
-[[package]]
-name = "zerocopy"
-version = "0.7.35"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1b9b4fd18abc82b8136838da5d50bae7bdea537c574d8dc1a34ed098d6c166f0"
-dependencies = [
- "zerocopy-derive 0.7.35",
-]
-
 [[package]]
 name = "zerocopy"
 version = "0.8.25"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a1702d9583232ddb9174e01bb7c15a2ab8fb1bc6f227aa1233858c351a3ba0cb"
 dependencies = [
- "zerocopy-derive 0.8.25",
-]
-
-[[package]]
-name = "zerocopy-derive"
-version = "0.7.35"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fa4f8080344d4671fb4e831a13ad1e68092748387dfc4f55e356242fae12ce3e"
-dependencies = [
- "proc-macro2",
- "quote",
- "syn 2.0.101",
+ "zerocopy-derive",
 ]
 
 [[package]]
@@ -8276,26 +8028,23 @@ name = "zeroize"
 version = "1.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ced3678a2879b30306d323f4542626697a464a97c0a07c9aebf7ebca65cd4dde"
-dependencies = [
- "zeroize_derive",
-]
 
 [[package]]
-name = "zeroize_derive"
-version = "1.4.2"
+name = "zerotrie"
+version = "0.2.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ce36e65b0d2999d2aafac989fb249189a141aee1f53c612c1f37d72631959f69"
+checksum = "36f0bbd478583f79edad978b407914f61b2972f5af6fa089686016be8f9af595"
 dependencies = [
- "proc-macro2",
- "quote",
- "syn 2.0.101",
+ "displaydoc",
+ "yoke",
+ "zerofrom",
 ]
 
 [[package]]
 name = "zerovec"
-version = "0.10.4"
+version = "0.11.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "aa2b893d79df23bfb12d5461018d408ea19dfafe76c2c7ef6d4eba614f8ff079"
+checksum = "4a05eb080e015ba39cc9e23bbe5e7fb04d5fb040350f99f34e338d5fdd294428"
 dependencies = [
  "yoke",
  "zerofrom",
@@ -8304,79 +8053,11 @@ dependencies = [
 
 [[package]]
 name = "zerovec-derive"
-version = "0.10.3"
+version = "0.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6eafa6dfb17584ea3e2bd6e76e0cc15ad7af12b09abdd1ca55961bed9b1063c6"
+checksum = "5b96237efa0c878c64bd89c436f661be4e46b2f3eff1ebb976f7ef2321d2f58f"
 dependencies = [
  "proc-macro2",
  "quote",
  "syn 2.0.101",
 ]
-
-[[package]]
-name = "zip"
-version = "2.6.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1dcb24d0152526ae49b9b96c1dcf71850ca1e0b882e4e28ed898a93c41334744"
-dependencies = [
- "aes",
- "arbitrary",
- "bzip2",
- "constant_time_eq 0.3.1",
- "crc32fast",
- "crossbeam-utils",
- "deflate64",
- "flate2",
- "getrandom 0.3.2",
- "hmac",
- "indexmap 2.9.0",
- "lzma-rs",
- "memchr",
- "pbkdf2",
- "sha1",
- "time",
- "xz2",
- "zeroize",
- "zopfli",
- "zstd",
-]
-
-[[package]]
-name = "zopfli"
-version = "0.8.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "edfc5ee405f504cd4984ecc6f14d02d55cfda60fa4b689434ef4102aae150cd7"
-dependencies = [
- "bumpalo",
- "crc32fast",
- "log",
- "simd-adler32",
-]
-
-[[package]]
-name = "zstd"
-version = "0.13.3"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e91ee311a569c327171651566e07972200e76fcfe2242a4fa446149a3881c08a"
-dependencies = [
- "zstd-safe",
-]
-
-[[package]]
-name = "zstd-safe"
-version = "7.2.4"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f49c4d5f0abb602a93fb8736af2a4f4dd9512e36f7f570d66e65ff867ed3b9d"
-dependencies = [
- "zstd-sys",
-]
-
-[[package]]
-name = "zstd-sys"
-version = "2.0.15+zstd.1.5.7"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "eb81183ddd97d0c74cedf1d50d85c8d08c1b8b68ee863bdee9e706eedba1a237"
-dependencies = [
- "cc",
- "pkg-config",
-]
```

### Cargo.toml
```diff
@@ -17,17 +17,16 @@ members = [
     "utils/validation",
     "binary_port",
     "smart_contracts/sdk",
-    "smart_contracts/sdk-codegen",
-    "smart_contracts/sdk-sys",
+    "smart_contracts/sdk_codegen",
+    "smart_contracts/sdk_sys",
     "smart_contracts/macros",
-    "cargo-casper",
-    "cargo-casper/project-template",
+    "cargo_casper",
     # "utils/highway-rewards-analysis",
     # "utils/highway-state-grapher",
-    "executor/wasm-common",
-    "executor/wasm-interface",
-    "executor/wasm-host",
-    "executor/wasmer-backend",
+    "executor/wasm_common",
+    "executor/wasm_interface",
+    "executor/wasm_host",
+    "executor/wasmer_backend",
     "executor/wasm",
 ]
 
@@ -43,8 +42,8 @@ default-members = [
     "utils/validation",
     "binary_port",
     "smart_contracts/sdk",
-    "smart_contracts/sdk-sys",
-    "smart_contracts/sdk-codegen",
+    "smart_contracts/sdk_sys",
+    "smart_contracts/sdk_codegen",
     "smart_contracts/macros",
     # "utils/highway-rewards-analysis",
     # "utils/highway-state-grapher",
```

### Makefile
```diff
@@ -20,7 +20,6 @@ CARGO_HOME_REMAP = $(if $(CARGO_HOME),$(CARGO_HOME),$(HOME)/.cargo)
 RUSTC_FLAGS      = "--remap-path-prefix=$(CARGO_HOME_REMAP)=/home/cargo --remap-path-prefix=$$PWD=/dir"
 
 CONTRACT_TARGET_DIR       = target/wasm32-unknown-unknown/release
-CONTRACT_TARGET_DIR_AS    = target_as
 
 build-contract-rs/%:
 	cd smart_contracts/contracts && RUSTFLAGS=$(RUSTC_FLAGS) $(CARGO) build --verbose --release $(filter-out --release, $(CARGO_FLAGS)) --package $*
```

### README.md
```diff
@@ -13,20 +13,17 @@ future-proof to support innovations today and tomorrow. Guided by open-source pr
 empower individuals, the team seeks to provide an equitable foundation made for long-lasting impact. Read more about our
 mission at: https://casper.network
 
-### Current Development Status
-The status on development is reported during the Community calls and is found [here](https://github.com/CasperLabs/Governance/wiki/Current-Status)
-
 The Casper MainNet is live.
 - [cspr.live Block Explorer](https://cspr.live)
 
 ### Specification
 
 - [Platform Specification](https://docs.casper.network/design)
-- [Highway Consensus Proofs](https://github.com/CasperLabs/highway/releases/latest)
+- [Highway Consensus Proofs](https://github.com/casper-network/highway/releases/latest)
 - [Zug Consensus Whitepaper](http://arxiv.org/pdf/2205.06314)
 
 ### Get Started with Smart Contracts
-- [Writing Smart Contracts](https://docs.casperlabs.io/developers/)
+- [Writing Smart Contracts](https://docs.casper.network/developers/)
 - [Rust Smart Contract SDK](https://crates.io/crates/cargo-casper)
 - [Rust Smart Contract API Docs](https://docs.rs/casper-contract/latest/casper_contract/contract_api/index.html)
 - [AssemblyScript Smart Contract API](https://www.npmjs.com/package/casper-contract)
@@ -35,6 +32,7 @@ The Casper MainNet is live.
 
 - [Discord Server](https://discord.gg/caspernetwork)
 - [Telegram Channel](https://t.me/casperofficialann)
+- [X (Twitter)](https://x.com/Casper_Network)
 
 
 
```

### binary_port/Cargo.toml
```diff
@@ -1,19 +1,19 @@
 [package]
 name = "casper-binary-port"
-version = "1.0.0"
+version = "1.1.0"
 edition = "2018"
 description = "Types for the casper node binary port"
 documentation = "https://docs.rs/casper-binary-port"
 readme = "README.md"
-homepage = "https://casperlabs.io"
+homepage = "https://casper.network"
 repository = "https://github.com/casper-network/casper-node/tree/master/binary_port"
 license = "Apache-2.0"
 exclude = ["proptest-regressions"]
 
 [dependencies]
 bincode = "1.3.3"
 bytes = "1.0.1"
-casper-types = { version = "5.0.1", path = "../types", features = ["datasize", "json-schema", "std"] }
+casper-types = { version = "6.0.0", path = "../types", features = ["datasize", "json-schema", "std"] }
 num-derive = { workspace = true }
 num-traits = { workspace = true }
 once_cell = { version = "1.5.2" }
```

### binary_port/README.md
```diff
@@ -2,14 +2,13 @@
 
 [![LOGO](https://raw.githubusercontent.com/casper-network/casper-node/master/images/casper-association-logo-primary.svg)](https://casper.network/)
 
-[![Build Status](https://drone-auto-casper-network.casperlabs.io/api/badges/casper-network/casper-node/status.svg?branch=dev)](http://drone-auto-casper-network.casperlabs.io/casper-network/casper-node)
 [![Crates.io](https://img.shields.io/crates/v/casper-hashing)](https://crates.io/crates/casper-binary-port)
 [![Documentation](https://docs.rs/casper-hashing/badge.svg)](https://docs.rs/casper-binary-port)
 [![License](https://img.shields.io/badge/license-Apache-blue)](https://github.com/casper-network/casper-node/blob/master/LICENSE)
 
 Types for the binary port on a casper network node.
 
-[Node Operator Guide](https://docs.casperlabs.io/operators/)
+[Node Operator Guide](https://docs.casper.network/operators/)
 
 ## License
 
```

### cargo-casper/project-template/Cargo.toml
```diff
@@ -1,11 +0,0 @@
-[package]
-name = "project-template"
-version = "0.1.0"
-edition = "2021"
-
-[lib]
-crate-type = ["cdylib", "rlib"]
-
-[dependencies]
-casper-macros = { git = "https://github.com/casper-network/casper-node.git", branch = "dev" }
-casper-sdk = { git = "https://github.com/casper-network/casper-node.git", branch = "dev" }
\ No newline at end of file
```

### cargo_casper/Cargo.toml
```diff
@@ -4,11 +4,11 @@ version = "0.1.0"
 edition = "2021"
 
 [dependencies]
+casper-contract-sdk-sys = { path = "../smart_contracts/sdk_sys" }
+casper-contract-sdk = { path = "../smart_contracts/sdk", features = ["__abi_generator"] }
 clap = { version = "4.4.11", features = ["derive"] }
 clap-cargo = { version = "0.14.0", features = ["cargo_metadata"] }
 libloading = "0.8.6"
-casper-sdk-sys = { path = "../smart_contracts/sdk-sys" }
-casper-sdk = { path = "../smart_contracts/sdk", features = ["__abi_generator"] }
 include_dir = "0.7.4"
 anyhow = "1.0.86"
 serde = { version = "1.0", features = ["derive"] }
```
