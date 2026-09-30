# [?] Upgrade zerocopy, fix RUSTSEC-2023-0074

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2023-12-19
Source: https://github.com/nervosnetwork/ckb/commit/0de0f1c84d09ec818af5341392c2d378558715ca
Type: security-commit

## Details
Upgrade zerocopy, fix RUSTSEC-2023-0074

## Patch
### Cargo.lock
```diff
@@ -5422,18 +5422,18 @@ checksum = "09041cd90cf85f7f8b2df60c646f853b7f535ce68f85244eb6731cf89fa498ec"
 
 [[package]]
 name = "zerocopy"
-version = "0.7.14"
+version = "0.7.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "69c48d63854f77746c68a5fbb4aa17f3997ece1cb301689a257af8cb80610d21"
+checksum = "1c4061bedbb353041c12f413700357bec76df2c7e2ca8e4df8bac24c6bf68e3d"
 dependencies = [
  "zerocopy-derive",
 ]
 
 [[package]]
 name = "zerocopy-derive"
-version = "0.7.14"
+version = "0.7.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c258c1040279e4f88763a113de72ce32dde2d50e2a94573f15dd534cea36a16d"
+checksum = "b3c129550b3e6de3fd0ba67ba5c81818f9805e58b8d7fee80a3a59d2c9fc601a"
 dependencies = [
  "proc-macro2",
  "quote",
```
