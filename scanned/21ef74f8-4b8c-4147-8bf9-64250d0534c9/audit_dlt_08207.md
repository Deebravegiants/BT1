# [?] deps: Upgrades h2 due to security advisory (#34816)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2024-01-18
Source: https://github.com/solana-labs/solana/commit/0e8f2de1da2e38451dfd4cc45aa51d10dfe428f1
Type: security-commit

## Details
deps: Upgrades h2 due to security advisory (#34816)

## Patch
### Cargo.lock
```diff
@@ -2298,17 +2298,17 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.3.18"
+version = "0.3.24"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "17f8a914c2987b688368b5138aa05321db91f4090cf26118185672ad588bce21"
+checksum = "bb2c4422095b67ee78da96fbb51a4cc413b3b25883c7717ff7ca1ab31022c9c9"
 dependencies = [
  "bytes",
  "fnv",
  "futures-core",
  "futures-sink",
  "futures-util",
  "http",
- "indexmap 1.9.3",
+ "indexmap 2.1.0",
  "slab",
  "tokio",
  "tokio-util 0.7.1",
@@ -8738,9 +8738,9 @@ checksum = "b6bc1c9ce2b5135ac7f93c72918fc37feb872bdc6a5533a8b85eb4b86bfdae52"
 
 [[package]]
 name = "tracing"
-version = "0.1.29"
+version = "0.1.35"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "375a639232caf30edfc78e8d89b2d4c375515393e7af7e16f01cd96917fb2105"
+checksum = "a400e31aa60b9d44a52a8ee0343b5b18566b03a8321e0d321f695cf56e940160"
 dependencies = [
  "cfg-if 1.0.0",
  "log",
@@ -8751,22 +8751,23 @@ dependencies = [
 
 [[package]]
 name = "tracing-attributes"
-version = "0.1.18"
+version = "0.1.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f4f480b8f81512e825f337ad51e94c1eb5d3bbdf2b363dcd01e2b19a9ffe3f8e"
+checksum = "34704c8d6ebcbc939824180af020566b01a7c01f80641264eba0999f6c2b6be7"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 1.0.109",
+ "syn 2.0.48",
 ]
 
 [[package]]
 name = "tracing-core"
-version = "0.1.21"
+version = "0.1.32"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1f4ed65637b8390770814083d20756f87bfa2c21bf2f110babdc5438351746e4"
+checksum = "c06d3da6113f116aaee68e4d601191614c9053067f9ab7f6edbcb161237daa54"
 dependencies = [
- "lazy_static",
+ "once_cell",
+ "valuable",
 ]
 
 [[package]]
@@ -8966,6 +8967,12 @@ version = "0.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7cf7d77f457ef8dfa11e4cd5933c5ddb5dc52a94664071951219a97710f0a32b"
 
+[[package]]
+name = "valuable"
+version = "0.1.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "830b7e5d4d90034032940e4ace0d9a9a057e7a45cd94e6c007832e39edb82f6d"
+
 [[package]]
 name = "vcpkg"
 version = "0.2.15"
```

### programs/sbf/Cargo.lock
```diff
@@ -1956,17 +1956,17 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.3.18"
+version = "0.3.24"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "17f8a914c2987b688368b5138aa05321db91f4090cf26118185672ad588bce21"
+checksum = "bb2c4422095b67ee78da96fbb51a4cc413b3b25883c7717ff7ca1ab31022c9c9"
 dependencies = [
  "bytes",
  "fnv",
  "futures-core",
  "futures-sink",
  "futures-util",
  "http",
- "indexmap 1.9.3",
+ "indexmap 2.1.0",
  "slab",
  "tokio",
  "tokio-util 0.7.1",
@@ -7598,9 +7598,9 @@ checksum = "b6bc1c9ce2b5135ac7f93c72918fc37feb872bdc6a5533a8b85eb4b86bfdae52"
 
 [[package]]
 name = "tracing"
-version = "0.1.29"
+version = "0.1.35"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "375a639232caf30edfc78e8d89b2d4c375515393e7af7e16f01cd96917fb2105"
+checksum = "a400e31aa60b9d44a52a8ee0343b5b18566b03a8321e0d321f695cf56e940160"
 dependencies = [
  "cfg-if 1.0.0",
  "log",
@@ -7611,22 +7611,22 @@ dependencies = [
 
 [[package]]
 name = "tracing-attributes"
-version = "0.1.18"
+version = "0.1.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f4f480b8f81512e825f337ad51e94c1eb5d3bbdf2b363dcd01e2b19a9ffe3f8e"
+checksum = "34704c8d6ebcbc939824180af020566b01a7c01f80641264eba0999f6c2b6be7"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 1.0.109",
+ "syn 2.0.48",
 ]
 
 [[package]]
 name = "tracing-core"
-version = "0.1.26"
+version = "0.1.32"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f54c8ca710e81886d498c2fd3331b56c93aa248d49de2222ad2742247c60072f"
+checksum = "c06d3da6113f116aaee68e4d601191614c9053067f9ab7f6edbcb161237daa54"
 dependencies = [
- "lazy_static",
+ "once_cell",
  "valuable",
 ]
 
```
