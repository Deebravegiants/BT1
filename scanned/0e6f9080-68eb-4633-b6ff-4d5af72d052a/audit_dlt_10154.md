# [?] chore(deps): bump generic-array from 0.12.3 to 0.12.4 to fix RUSTSEC-2020-0146

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-03-03
Source: https://github.com/nervosnetwork/ckb/commit/1c3182d4f9bede7acbcc121a2311e6045a5f61b2
Type: security-commit

## Details
chore(deps): bump generic-array from 0.12.3 to 0.12.4 to fix RUSTSEC-2020-0146

## Patch
### Cargo.lock
```diff
@@ -221,7 +221,7 @@ dependencies = [
  "block-padding",
  "byte-tools",
  "byteorder",
- "generic-array 0.12.3",
+ "generic-array 0.12.4",
 ]
 
 [[package]]
@@ -1844,7 +1844,7 @@ version = "0.8.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "05f47366984d3ad862010e22c7ce81a7dbcaebbdfb37241a620f8b6596ee135c"
 dependencies = [
- "generic-array 0.12.3",
+ "generic-array 0.12.4",
 ]
 
 [[package]]
@@ -2159,9 +2159,9 @@ dependencies = [
 
 [[package]]
 name = "generic-array"
-version = "0.12.3"
+version = "0.12.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c68f0274ae0e023facc3c97b2e00f076be70e254bc851d972503b328db79b2ec"
+checksum = "ffdf9f34f1447443d37393cc6c2b8313aebddcd96906caf34e54c68d8e57d7bd"
 dependencies = [
  "typenum",
 ]
```
