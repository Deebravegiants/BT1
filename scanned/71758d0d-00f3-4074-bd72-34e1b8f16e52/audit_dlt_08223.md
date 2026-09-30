# [?] Address RUSTSEC-2022-0051

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2022-08-26
Source: https://github.com/solana-labs/solana/commit/05fe061a7c9c68c95cbab6378ce920f63ffe1874
Type: security-commit

## Details
Address RUSTSEC-2022-0051

`lz4` to 1.24.0
`lz4-sys` to 1.9.4

## Patch
### Cargo.lock
```diff
@@ -2557,19 +2557,19 @@ dependencies = [
 
 [[package]]
 name = "lz4"
-version = "1.23.3"
+version = "1.24.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4edcb94251b1c375c459e5abe9fb0168c1c826c3370172684844f8f3f8d1a885"
+checksum = "7e9e2dd86df36ce760a60f6ff6ad526f7ba1f14ba0356f8254fb6905e6494df1"
 dependencies = [
  "libc",
  "lz4-sys",
 ]
 
 [[package]]
 name = "lz4-sys"
-version = "1.9.3"
+version = "1.9.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d7be8908e2ed6f31c02db8a9fa962f03e36c53fbfde437363eae3306b85d7e17"
+checksum = "57d27b317e207b10f69f5e75494119e391a96f48861ae870d1da6edac98ca900"
 dependencies = [
  "cc",
  "libc",
```

### programs/bpf/Cargo.lock
```diff
@@ -2348,19 +2348,19 @@ dependencies = [
 
 [[package]]
 name = "lz4"
-version = "1.23.3"
+version = "1.24.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4edcb94251b1c375c459e5abe9fb0168c1c826c3370172684844f8f3f8d1a885"
+checksum = "7e9e2dd86df36ce760a60f6ff6ad526f7ba1f14ba0356f8254fb6905e6494df1"
 dependencies = [
  "libc",
  "lz4-sys",
 ]
 
 [[package]]
 name = "lz4-sys"
-version = "1.9.3"
+version = "1.9.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d7be8908e2ed6f31c02db8a9fa962f03e36c53fbfde437363eae3306b85d7e17"
+checksum = "57d27b317e207b10f69f5e75494119e391a96f48861ae870d1da6edac98ca900"
 dependencies = [
  "cc",
  "libc",
```

### runtime/Cargo.toml
```diff
@@ -27,7 +27,7 @@ index_list = "0.2.7"
 itertools = "0.10.3"
 lazy_static = "1.4.0"
 log = "0.4.17"
-lz4 = "1.23.3"
+lz4 = "1.24.0"
 memmap2 = "0.5.3"
 num-derive = { version = "0.3" }
 num-traits = { version = "0.2" }
```
