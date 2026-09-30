# [?] Fixed overflows v3.0.x (#2662)

## Summary
Severity: Unknown
Chain: Cosmos
Component: CosmWasm/cosmwasm
Published: 2026-05-13
Source: https://github.com/CosmWasm/cosmwasm/commit/355eea5ca6d93d6fc28d487887d26aabe1095721
Type: security-commit

## Details
Fixed overflows v3.0.x (#2662)

## Patch
### CHANGELOG.md
```diff
@@ -6,6 +6,14 @@ The format is based on [Keep a Changelog], and this project adheres to [Semantic
 
 (empty)
 
+## [3.0.6] - 2025-05-13
+
+- Bumped version in README. ([#2648])
+- Fixed overflows v3.0.x ([#2662])
+
+[#2648]: https://github.com/CosmWasm/cosmwasm/pull/2648
+[#2662]: https://github.com/CosmWasm/cosmwasm/pull/2662
+
 ## [3.0.5] - 2025-04-24
 
 - Fixes to IBCv2 async acks ([#2646])
@@ -306,6 +314,16 @@ The format is based on [Keep a Changelog], and this project adheres to [Semantic
 [#2500]: https://github.com/CosmWasm/cosmwasm/pull/2500
 [#2501]: https://github.com/CosmWasm/cosmwasm/pull/2501
 
+## [2.3.3] - 2026-05-13
+
+- Replaced deprecated code of `assert_cmd` in v2.3.x ([#2618])
+- Refactored `cosmwasm-check` tests in v2.3.x ([#2621])
+- Fixed overflows v2.3.x ([#2661])
+
+[#2618]: https://github.com/CosmWasm/cosmwasm/pull/2618
+[#2621]: https://github.com/CosmWasm/cosmwasm/pull/2621
+[#2661]: https://github.com/CosmWasm/cosmwasm/pull/2661
+
 ## [2.3.2] - 2026-02-11
 
 - Prepared version v2.3.2 ([#2612])
@@ -1548,16 +1566,19 @@ The format is based on [Keep a Changelog], and this project adheres to [Semantic
 The CHANGELOG for versions before **1.0.0** was moved to
 [CHANGELOG-pre-1.0.0.md](./CHANGELOG-pre-1.0.0.md).
 
-[Unreleased]: https://github.com/CosmWasm/cosmwasm/compare/v3.0.5...HEAD
+[Unreleased]: https://github.com/CosmWasm/cosmwasm/compare/v3.0.6...HEAD
+[3.0.6]: https://github.com/CosmWasm/cosmwasm/compare/v3.0.5...v3.0.6
 [3.0.5]: https://github.com/CosmWasm/cosmwasm/compare/v3.0.4...v3.0.5
 [3.0.4]: https://github.com/CosmWasm/cosmwasm/compare/v3.0.3...v3.0.4
 [3.0.3]: https://github.com/CosmWasm/cosmwasm/compare/v3.0.2...v3.0.3
 [3.0.2]: https://github.com/CosmWasm/cosmwasm/compare/v3.0.1...v3.0.2
 [3.0.1]: https://github.com/CosmWasm/cosmwasm/compare/v3.0.0...v3.0.1
-[3.0.0]: https://github.com/CosmWasm/cosmwasm/compare/v2.2.0...v3.0.0
+[3.0.0]: https://github.com/CosmWasm/cosmwasm/compare/v2.3.3...v3.0.0
+[2.3.3]: https://github.com/CosmWasm/cosmwasm/compare/v2.3.2...v2.3.3
 [2.3.2]: https://github.com/CosmWasm/cosmwasm/compare/v2.3.1...v2.3.2
 [2.3.1]: https://github.com/CosmWasm/cosmwasm/compare/v2.3.0...v2.3.1
-[2.3.0]: https://github.com/CosmWasm/cosmwasm/compare/v2.2.2...v2.3.0
+[2.3.0]: https://github.com/CosmWasm/cosmwasm/compare/v2.2.8...v2.3.0
+[2.2.8]: https://github.com/CosmWasm/cosmwasm/compare/v2.2.7...v2.2.8
 [2.2.7]: https://github.com/CosmWasm/cosmwasm/compare/v2.2.6...v2.2.7
 [2.2.6]: https://github.com/CosmWasm/cosmwasm/compare/v2.2.3...v2.2.6
 [2.2.3]: https://github.com/CosmWasm/cosmwasm/compare/v2.2.2...v2.2.3
```

### Cargo.lock
```diff
@@ -619,39 +619,39 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-check"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
  "anyhow",
  "assert_cmd",
  "clap",
  "colored",
- "cosmwasm-std 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-vm 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-std 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-vm 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "predicates",
  "tempfile",
 ]
 
 [[package]]
 name = "cosmwasm-core"
-version = "3.0.5"
+version = "3.0.6"
 
 [[package]]
 name = "cosmwasm-core"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bb372d91a06c6ad130559c9028048c92a557ec4f466b00a49cbd5e79f5e2880b"
+checksum = "53ad3b5a29aa6c01402bdc1798cef984d973353ebe8d206a56545d4b7d2e2378"
 
 [[package]]
 name = "cosmwasm-crypto"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
  "ark-bls12-381",
  "ark-ec",
  "ark-ff",
  "ark-serialize",
  "base64 0.22.1",
  "base64-serde",
- "cosmwasm-core 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-core 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "criterion",
  "curve25519-dalek",
  "digest",
@@ -676,15 +676,15 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-crypto"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5c1731c775eb882e6cc3f295e0b91f32c9f7e40b6c1157d04029dd781bbe5b4d"
+checksum = "3655749727db6d7e2ec5deee87db2fde8a2d398c0027a1b256a73ebc2c2c8cdd"
 dependencies = [
  "ark-bls12-381",
  "ark-ec",
  "ark-ff",
  "ark-serialize",
- "cosmwasm-core 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-core 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "curve25519-dalek",
  "digest",
  "ecdsa",
@@ -701,7 +701,7 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-derive"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -710,9 +710,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5a453265d2883bece23abac6b8fe1cc85b130d0ef8a70c842c1731a5647d8e39"
+checksum = "202773f92acc668a8a0a06338e3a68588bf5cc797b3922aa3e890aaedfe8744a"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -721,11 +721,11 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
  "anyhow",
- "cosmwasm-schema-derive 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cw-schema 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-schema-derive 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cw-schema 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "insta",
  "schemars 0.8.22",
  "semver",
@@ -737,12 +737,12 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6e7a343f87b7088d758ef6566d0d23ade6a7fb272f40ba8abeb10599a61190cf"
+checksum = "073fa31d0ee9824fb5a56f01bbc9ee6f597882f6a80e838b7d879325e9948c7e"
 dependencies = [
- "cosmwasm-schema-derive 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cw-schema 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-schema-derive 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cw-schema 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "schemars 0.8.22",
  "serde",
  "serde_json",
@@ -751,7 +751,7 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -760,9 +760,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9efc561a05c244ca92663a885c32f64048ba5a1d80d10a575f4af63d0b1c5a3c"
+checksum = "d87d8104ba397b2c7294299630a8309a0e7428a9ce117a335e41ca97d5385ea5"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -771,18 +771,18 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-std"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
  "base64 0.22.1",
  "bech32",
  "bnum",
  "chrono",
- "cosmwasm-core 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-crypto 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-derive 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-schema 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-core 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-crypto 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-derive 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-schema 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "crc32fast",
- "cw-schema 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cw-schema 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "derive_more 2.0.1",
  "hex",
  "hex-literal",
@@ -800,17 +800,17 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-std"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5420f6d4181383fe5894609f8dfa54ce4c494ae8fafe5d30eaa7516ee984bdc8"
+checksum = "4e4bcfe974bb8e539c7b6f1a7693d779f5755569c11957e778a97e6f50ffeb6b"
 dependencies = [
  "base64 0.22.1",
  "bech32",
  "bnum",
- "cosmwasm-core 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-crypto 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-derive 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cw-schema 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-core 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-crypto 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-derive 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cw-schema 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "derive_more 2.0.1",
  "hex",
  "rand_core 0.6.4",
@@ -825,17 +825,17 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
  "bech32",
  "blake2",
  "bytes",
  "clap",
  "clru",
- "cosmwasm-core 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-crypto 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-std 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-vm-derive 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-core 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-crypto 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-std 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-vm-derive 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "crc32fast",
  "criterion",
  "derive_more 1.0.0-beta.6",
@@ -864,18 +864,18 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9e78e4556521898d175c0dd5203fee3757198cee255cd4522f3024c09695101c"
+checksum = "f0ff2d2461986f9b6fc9fb6a2567176283a354883cd5b92b9ea59aaa95a5bc1f"
 dependencies = [
  "bech32",
  "blake2",
  "bytes",
  "clru",
- "cosmwasm-core 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-crypto 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-std 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-vm-derive 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-core 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-crypto 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-std 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-vm-derive 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "crc32fast",
  "derive_more 1.0.0-beta.6",
  "hex",
@@ -893,7 +893,7 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm-derive"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
  "blake2",
  "proc-macro2",
@@ -903,9 +903,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "27e4b2b44579f9d7cbe9006e8fdaf214226f84b7e5abb71cfc2e39d3909fb571"
+checksum = "f26a01bd71ea378986e2791d7407e6edb718e332f5b7d952a78e172cd1b4cde4"
 dependencies = [
  "blake2",
  "proc-macro2",
@@ -1058,9 +1058,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
- "cw-schema-derive 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cw-schema-derive 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "indexmap",
  "insta",
  "pretty_assertions",
@@ -1074,11 +1074,11 @@ dependencies = [
 
 [[package]]
 name = "cw-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "03fdbf30558ff380a9555b508b3b68f60ab205cb93c6f34de2bfef27ee5eeee5"
+checksum = "ae6ee893f829ea7ccfe72bb4978bc989442837bd01236a52a1f8ae3da56e57ad"
 dependencies = [
- "cw-schema-derive 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cw-schema-derive 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "indexmap",
  "schemars 1.0.4",
  "serde",
@@ -1089,7 +1089,7 @@ dependencies = [
 
 [[package]]
 name = "cw-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 dependencies = [
  "heck",
  "itertools 0.13.0",
@@ -1101,9 +1101,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a978316851c7855bacb73844c71d1d9ab5f999b7c75fe0863042d61f721d3b99"
+checksum = "e873affc75b36e7c24e55b65ee17af1b71a60a6e15c9a191d1aa9805a17e413a"
 dependencies = [
  "heck",
  "itertools 0.13.0",
@@ -1623,8 +1623,8 @@ name = "go-gen"
 version = "0.1.0"
 dependencies = [
  "anyhow",
- "cosmwasm-schema 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
- "cosmwasm-std 3.0.5 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-schema 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
+ "cosmwasm-std 3.0.6 (registry+https://github.com/rust-lang/crates.io-index)",
  "heck",
  "indenter",
  "schemars 0.8.22",
```

### Cargo.toml
```diff
@@ -5,23 +5,23 @@ exclude = ["contracts"]
 resolver = "2"
 
 [workspace.package]
-version = "3.0.5"
+version = "3.0.6"
 edition = "2021"
 license = "Apache-2.0"
 repository = "https://github.com/CosmWasm/cosmwasm"
 
 [workspace.dependencies]
-cosmwasm-core = { version = "3.0.5" }
-cosmwasm-crypto = { version = "3.0.5" }
-cosmwasm-derive = { version = "3.0.5" }
-cosmwasm-schema = { version = "3.0.5" }
-cosmwasm-schema-derive = { version = "3.0.5" }
-cosmwasm-std = { version = "3.0.5", default-features = false }
-cosmwasm-vm = { version = "3.0.5" }
-cosmwasm-vm-derive = { version = "3.0.5" }
-cw-schema = { version = "3.0.5" }
-cw-schema-derive = { version = "3.0.5" }
-cosmwasm-check = { version = "3.0.5" }
+cosmwasm-core = { version = "3.0.6" }
+cosmwasm-crypto = { version = "3.0.6" }
+cosmwasm-derive = { version = "3.0.6" }
+cosmwasm-schema = { version = "3.0.6" }
+cosmwasm-schema-derive = { version = "3.0.6" }
+cosmwasm-std = { version = "3.0.6", default-features = false }
+cosmwasm-vm = { version = "3.0.6" }
+cosmwasm-vm-derive = { version = "3.0.6" }
+cw-schema = { version = "3.0.6" }
+cw-schema-derive = { version = "3.0.6" }
+cosmwasm-check = { version = "3.0.6" }
 schemars = "0.8.4"
 serde = { version = "1.0.192", default-features = false, features = ["alloc", "derive"] }
 serde_json = "1.0.140"
```

### README.md
```diff
@@ -120,37 +120,37 @@ config:
 
 graph BT
     A("`**cosmwasm-core**
-        3.0.5`")
+        3.0.6`")
  
     B("`**cosmwasm-std**
-        3.0.5`")
+        3.0.6`")
  
     C("`**cosmwasm-crypto**
-        3.0.5`")
+        3.0.6`")
         
     D("`**cosmwasm-vm**
-        3.0.5`")
+        3.0.6`")
         
     E("`**cosmwasm-vm-derive**
-        3.0.5`")
+        3.0.6`")
         
     F("`**cosmwasm-derive**
-        3.0.5`")
+        3.0.6`")
         
     G("`**cosmwasm-schema**
-        3.0.5`")
+        3.0.6`")
 
     H("`**cosmwasm-schema-derive**
-        3.0.5`")
+        3.0.6`")
         
     I("`**cosmwasm-check**
-        3.0.5`")
+        3.0.6`")
         
     J("`**cw-schema**
-        3.0.5`")
+        3.0.6`")
 
     K("`**cw-schema-derive**
-        3.0.5`")
+        3.0.6`")
         
     A --> B
     A --> C
```

### Taskfile.yml
```diff
@@ -3,7 +3,7 @@ version: '3'
 silent: true
 
 vars:
-  COSMWASM_CHECK_VERSION: 3.0.4 # The last released version of cosmwasm-check tool before 3.0.3.
+  COSMWASM_CHECK_VERSION: 3.0.5 # The last released version of cosmwasm-check tool before 3.0.6.
   TOOLCHAIN: +1.82.0            # Rust toolchain for building packages.
   TOOLCHAIN_CHECK: +1.82.0      # Rust toolchain for building cosmwasm-check tool.
 
```

### contracts/burner/Cargo.lock
```diff
@@ -425,15 +425,15 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-core"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bb372d91a06c6ad130559c9028048c92a557ec4f466b00a49cbd5e79f5e2880b"
+checksum = "53ad3b5a29aa6c01402bdc1798cef984d973353ebe8d206a56545d4b7d2e2378"
 
 [[package]]
 name = "cosmwasm-crypto"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5c1731c775eb882e6cc3f295e0b91f32c9f7e40b6c1157d04029dd781bbe5b4d"
+checksum = "3655749727db6d7e2ec5deee87db2fde8a2d398c0027a1b256a73ebc2c2c8cdd"
 dependencies = [
  "ark-bls12-381",
  "ark-ec",
@@ -456,9 +456,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5a453265d2883bece23abac6b8fe1cc85b130d0ef8a70c842c1731a5647d8e39"
+checksum = "202773f92acc668a8a0a06338e3a68588bf5cc797b3922aa3e890aaedfe8744a"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -467,9 +467,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6e7a343f87b7088d758ef6566d0d23ade6a7fb272f40ba8abeb10599a61190cf"
+checksum = "073fa31d0ee9824fb5a56f01bbc9ee6f597882f6a80e838b7d879325e9948c7e"
 dependencies = [
  "cosmwasm-schema-derive",
  "cw-schema",
@@ -481,9 +481,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9efc561a05c244ca92663a885c32f64048ba5a1d80d10a575f4af63d0b1c5a3c"
+checksum = "d87d8104ba397b2c7294299630a8309a0e7428a9ce117a335e41ca97d5385ea5"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -492,9 +492,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-std"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5420f6d4181383fe5894609f8dfa54ce4c494ae8fafe5d30eaa7516ee984bdc8"
+checksum = "4e4bcfe974bb8e539c7b6f1a7693d779f5755569c11957e778a97e6f50ffeb6b"
 dependencies = [
  "base64",
  "bech32",
@@ -517,9 +517,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9e78e4556521898d175c0dd5203fee3757198cee255cd4522f3024c09695101c"
+checksum = "f0ff2d2461986f9b6fc9fb6a2567176283a354883cd5b92b9ea59aaa95a5bc1f"
 dependencies = [
  "bech32",
  "blake2",
@@ -546,9 +546,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "27e4b2b44579f9d7cbe9006e8fdaf214226f84b7e5abb71cfc2e39d3909fb571"
+checksum = "f26a01bd71ea378986e2791d7407e6edb718e332f5b7d952a78e172cd1b4cde4"
 dependencies = [
  "blake2",
  "proc-macro2",
@@ -659,9 +659,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "03fdbf30558ff380a9555b508b3b68f60ab205cb93c6f34de2bfef27ee5eeee5"
+checksum = "ae6ee893f829ea7ccfe72bb4978bc989442837bd01236a52a1f8ae3da56e57ad"
 dependencies = [
  "cw-schema-derive",
  "indexmap",
@@ -674,9 +674,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a978316851c7855bacb73844c71d1d9ab5f999b7c75fe0863042d61f721d3b99"
+checksum = "e873affc75b36e7c24e55b65ee17af1b71a60a6e15c9a191d1aa9805a17e413a"
 dependencies = [
  "heck",
  "itertools",
```

### contracts/burner/Cargo.toml
```diff
@@ -24,10 +24,10 @@ incremental = false
 overflow-checks = true
 
 [dependencies]
-cosmwasm-schema = { version = "3.0.5" }
-cosmwasm-std = { version = "3.0.5", features = ["cosmwasm_1_4", "iterator"] }
+cosmwasm-schema = { version = "3.0.6" }
+cosmwasm-std = { version = "3.0.6", features = ["cosmwasm_1_4", "iterator"] }
 schemars = "0.8.12"
 serde = { version = "1.0.103", default-features = false, features = ["derive"] }
 
 [dev-dependencies]
-cosmwasm-vm = { version = "3.0.5", default-features = false, features = ["iterator"] }
+cosmwasm-vm = { version = "3.0.6", default-features = false, features = ["iterator"] }
```

### contracts/crypto-verify/Cargo.lock
```diff
@@ -420,15 +420,15 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-core"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bb372d91a06c6ad130559c9028048c92a557ec4f466b00a49cbd5e79f5e2880b"
+checksum = "53ad3b5a29aa6c01402bdc1798cef984d973353ebe8d206a56545d4b7d2e2378"
 
 [[package]]
 name = "cosmwasm-crypto"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5c1731c775eb882e6cc3f295e0b91f32c9f7e40b6c1157d04029dd781bbe5b4d"
+checksum = "3655749727db6d7e2ec5deee87db2fde8a2d398c0027a1b256a73ebc2c2c8cdd"
 dependencies = [
  "ark-bls12-381",
  "ark-ec",
@@ -451,9 +451,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5a453265d2883bece23abac6b8fe1cc85b130d0ef8a70c842c1731a5647d8e39"
+checksum = "202773f92acc668a8a0a06338e3a68588bf5cc797b3922aa3e890aaedfe8744a"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -462,9 +462,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6e7a343f87b7088d758ef6566d0d23ade6a7fb272f40ba8abeb10599a61190cf"
+checksum = "073fa31d0ee9824fb5a56f01bbc9ee6f597882f6a80e838b7d879325e9948c7e"
 dependencies = [
  "cosmwasm-schema-derive",
  "cw-schema",
@@ -476,9 +476,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9efc561a05c244ca92663a885c32f64048ba5a1d80d10a575f4af63d0b1c5a3c"
+checksum = "d87d8104ba397b2c7294299630a8309a0e7428a9ce117a335e41ca97d5385ea5"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -487,9 +487,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-std"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5420f6d4181383fe5894609f8dfa54ce4c494ae8fafe5d30eaa7516ee984bdc8"
+checksum = "4e4bcfe974bb8e539c7b6f1a7693d779f5755569c11957e778a97e6f50ffeb6b"
 dependencies = [
  "base64",
  "bech32",
@@ -512,9 +512,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9e78e4556521898d175c0dd5203fee3757198cee255cd4522f3024c09695101c"
+checksum = "f0ff2d2461986f9b6fc9fb6a2567176283a354883cd5b92b9ea59aaa95a5bc1f"
 dependencies = [
  "bech32",
  "blake2",
@@ -541,9 +541,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "27e4b2b44579f9d7cbe9006e8fdaf214226f84b7e5abb71cfc2e39d3909fb571"
+checksum = "f26a01bd71ea378986e2791d7407e6edb718e332f5b7d952a78e172cd1b4cde4"
 dependencies = [
  "blake2",
  "proc-macro2",
@@ -672,9 +672,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "03fdbf30558ff380a9555b508b3b68f60ab205cb93c6f34de2bfef27ee5eeee5"
+checksum = "ae6ee893f829ea7ccfe72bb4978bc989442837bd01236a52a1f8ae3da56e57ad"
 dependencies = [
  "cw-schema-derive",
  "indexmap",
@@ -687,9 +687,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a978316851c7855bacb73844c71d1d9ab5f999b7c75fe0863042d61f721d3b99"
+checksum = "e873affc75b36e7c24e55b65ee17af1b71a60a6e15c9a191d1aa9805a17e413a"
 dependencies = [
  "heck",
  "itertools",
```

### contracts/crypto-verify/Cargo.toml
```diff
@@ -22,8 +22,8 @@ overflow-checks = true
 
 [dependencies]
 base64 = "0.22.0"
-cosmwasm-schema = { version = "3.0.5" }
-cosmwasm-std = { version = "3.0.5", features = ["cosmwasm_2_1", "iterator"] }
+cosmwasm-schema = { version = "3.0.6" }
+cosmwasm-std = { version = "3.0.6", features = ["cosmwasm_2_1", "iterator"] }
 hex = "0.4"
 p256 = { version = "0.13.2", default-features = false, features = ["alloc", "ecdsa"] }
 rlp = "0.5"
@@ -33,5 +33,5 @@ sha2 = "0.10"
 sha3 = "0.10"
 
 [dev-dependencies]
-cosmwasm-vm = { version = "3.0.5", default-features = false, features = ["iterator"] }
+cosmwasm-vm = { version = "3.0.6", default-features = false, features = ["iterator"] }
 hex-literal = "0.4.1"
```

### contracts/cyberpunk/Cargo.lock
```diff
@@ -443,15 +443,15 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-core"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bb372d91a06c6ad130559c9028048c92a557ec4f466b00a49cbd5e79f5e2880b"
+checksum = "53ad3b5a29aa6c01402bdc1798cef984d973353ebe8d206a56545d4b7d2e2378"
 
 [[package]]
 name = "cosmwasm-crypto"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5c1731c775eb882e6cc3f295e0b91f32c9f7e40b6c1157d04029dd781bbe5b4d"
+checksum = "3655749727db6d7e2ec5deee87db2fde8a2d398c0027a1b256a73ebc2c2c8cdd"
 dependencies = [
  "ark-bls12-381",
  "ark-ec",
@@ -474,9 +474,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5a453265d2883bece23abac6b8fe1cc85b130d0ef8a70c842c1731a5647d8e39"
+checksum = "202773f92acc668a8a0a06338e3a68588bf5cc797b3922aa3e890aaedfe8744a"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -485,9 +485,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6e7a343f87b7088d758ef6566d0d23ade6a7fb272f40ba8abeb10599a61190cf"
+checksum = "073fa31d0ee9824fb5a56f01bbc9ee6f597882f6a80e838b7d879325e9948c7e"
 dependencies = [
  "cosmwasm-schema-derive",
  "cw-schema",
@@ -499,9 +499,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9efc561a05c244ca92663a885c32f64048ba5a1d80d10a575f4af63d0b1c5a3c"
+checksum = "d87d8104ba397b2c7294299630a8309a0e7428a9ce117a335e41ca97d5385ea5"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -510,9 +510,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-std"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5420f6d4181383fe5894609f8dfa54ce4c494ae8fafe5d30eaa7516ee984bdc8"
+checksum = "4e4bcfe974bb8e539c7b6f1a7693d779f5755569c11957e778a97e6f50ffeb6b"
 dependencies = [
  "base64 0.22.1",
  "bech32",
@@ -535,9 +535,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9e78e4556521898d175c0dd5203fee3757198cee255cd4522f3024c09695101c"
+checksum = "f0ff2d2461986f9b6fc9fb6a2567176283a354883cd5b92b9ea59aaa95a5bc1f"
 dependencies = [
  "bech32",
  "blake2",
@@ -564,9 +564,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "27e4b2b44579f9d7cbe9006e8fdaf214226f84b7e5abb71cfc2e39d3909fb571"
+checksum = "f26a01bd71ea378986e2791d7407e6edb718e332f5b7d952a78e172cd1b4cde4"
 dependencies = [
  "blake2",
  "proc-macro2",
@@ -677,9 +677,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "03fdbf30558ff380a9555b508b3b68f60ab205cb93c6f34de2bfef27ee5eeee5"
+checksum = "ae6ee893f829ea7ccfe72bb4978bc989442837bd01236a52a1f8ae3da56e57ad"
 dependencies = [
  "cw-schema-derive",
  "indexmap",
@@ -692,9 +692,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a978316851c7855bacb73844c71d1d9ab5f999b7c75fe0863042d61f721d3b99"
+checksum = "e873affc75b36e7c24e55b65ee17af1b71a60a6e15c9a191d1aa9805a17e413a"
 dependencies = [
  "heck",
  "itertools",
```

### contracts/cyberpunk/Cargo.toml
```diff
@@ -21,11 +21,11 @@ incremental = false
 overflow-checks = true
 
 [dependencies]
-cosmwasm-schema = { version = "3.0.5" }
-cosmwasm-std = { version = "3.0.5", default-features = false, features = ["cosmwasm_1_3", "exports", "std"] }
+cosmwasm-schema = { version = "3.0.6" }
+cosmwasm-std = { version = "3.0.6", default-features = false, features = ["cosmwasm_1_3", "exports", "std"] }
 rust-argon2 = "2.1"
 thiserror = "1.0.26"
 
 [dev-dependencies]
-cosmwasm-vm = { version = "3.0.5", default-features = false }
+cosmwasm-vm = { version = "3.0.6", default-features = false }
 tempfile = "3.1.0"
```

### contracts/empty/Cargo.lock
```diff
@@ -414,15 +414,15 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-core"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bb372d91a06c6ad130559c9028048c92a557ec4f466b00a49cbd5e79f5e2880b"
+checksum = "53ad3b5a29aa6c01402bdc1798cef984d973353ebe8d206a56545d4b7d2e2378"
 
 [[package]]
 name = "cosmwasm-crypto"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5c1731c775eb882e6cc3f295e0b91f32c9f7e40b6c1157d04029dd781bbe5b4d"
+checksum = "3655749727db6d7e2ec5deee87db2fde8a2d398c0027a1b256a73ebc2c2c8cdd"
 dependencies = [
  "ark-bls12-381",
  "ark-ec",
@@ -445,9 +445,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5a453265d2883bece23abac6b8fe1cc85b130d0ef8a70c842c1731a5647d8e39"
+checksum = "202773f92acc668a8a0a06338e3a68588bf5cc797b3922aa3e890aaedfe8744a"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -456,9 +456,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6e7a343f87b7088d758ef6566d0d23ade6a7fb272f40ba8abeb10599a61190cf"
+checksum = "073fa31d0ee9824fb5a56f01bbc9ee6f597882f6a80e838b7d879325e9948c7e"
 dependencies = [
  "cosmwasm-schema-derive",
  "cw-schema",
@@ -470,9 +470,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9efc561a05c244ca92663a885c32f64048ba5a1d80d10a575f4af63d0b1c5a3c"
+checksum = "d87d8104ba397b2c7294299630a8309a0e7428a9ce117a335e41ca97d5385ea5"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -481,9 +481,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-std"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5420f6d4181383fe5894609f8dfa54ce4c494ae8fafe5d30eaa7516ee984bdc8"
+checksum = "4e4bcfe974bb8e539c7b6f1a7693d779f5755569c11957e778a97e6f50ffeb6b"
 dependencies = [
  "base64",
  "bech32",
@@ -506,9 +506,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9e78e4556521898d175c0dd5203fee3757198cee255cd4522f3024c09695101c"
+checksum = "f0ff2d2461986f9b6fc9fb6a2567176283a354883cd5b92b9ea59aaa95a5bc1f"
 dependencies = [
  "bech32",
  "blake2",
@@ -535,9 +535,9 @@ dependencies = [
 
 [[package]]
 name = "cosmwasm-vm-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "27e4b2b44579f9d7cbe9006e8fdaf214226f84b7e5abb71cfc2e39d3909fb571"
+checksum = "f26a01bd71ea378986e2791d7407e6edb718e332f5b7d952a78e172cd1b4cde4"
 dependencies = [
  "blake2",
  "proc-macro2",
@@ -648,9 +648,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "03fdbf30558ff380a9555b508b3b68f60ab205cb93c6f34de2bfef27ee5eeee5"
+checksum = "ae6ee893f829ea7ccfe72bb4978bc989442837bd01236a52a1f8ae3da56e57ad"
 dependencies = [
  "cw-schema-derive",
  "indexmap",
@@ -663,9 +663,9 @@ dependencies = [
 
 [[package]]
 name = "cw-schema-derive"
-version = "3.0.5"
+version = "3.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a978316851c7855bacb73844c71d1d9ab5f999b7c75fe0863042d61f721d3b99"
+checksum = "e873affc75b36e7c24e55b65ee17af1b71a60a6e15c9a191d1aa9805a17e413a"
 dependencies = [
  "heck",
  "itertools",
```
