# [?] fix: fix RUSTSEC-2024-0402 (#9141)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2025-01-22
Source: https://github.com/ZcashFoundation/zebra/commit/c537bae35242b05baeeacbfc87d7596be95ddc64
Type: security-commit

## Details
fix: fix RUSTSEC-2024-0402 (#9141)

## Patch
### Cargo.lock
```diff
@@ -1664,9 +1664,9 @@ dependencies = [
 
 [[package]]
 name = "hashbrown"
-version = "0.15.0"
+version = "0.15.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1e087f84d4f86bf4b218b927129862374b72199ae7d8657835f1e89000eea4fb"
+checksum = "bf151400ff0baff5465007dd2f3e717f3fe502074ca563069ce3a6629d07b289"
 dependencies = [
  "foldhash",
 ]
@@ -2006,7 +2006,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "62f822373a4fe84d4bb149bf54e584a7f4abec90e072ed49cda0edea5b95471f"
 dependencies = [
  "equivalent",
- "hashbrown 0.15.0",
+ "hashbrown 0.15.2",
  "serde",
 ]
 
@@ -2477,7 +2477,7 @@ checksum = "15b482df36c13dd1869d73d14d28cd4855fbd6cfc32294bee109908a9f4a4ed7"
 dependencies = [
  "crossbeam-epoch",
  "crossbeam-utils",
- "hashbrown 0.15.0",
+ "hashbrown 0.15.2",
  "metrics",
  "quanta",
  "sketches-ddsketch",
```
