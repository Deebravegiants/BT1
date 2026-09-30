# [?] Revert "Bump `curve25519-dalek` and remove `RUSTSEC-2024-0344`"

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2024-06-20
Source: https://github.com/casper-network/casper-node/commit/9c3d800fe3022b087bc107c9a238c6a413447864
Type: security-commit

## Details
Revert "Bump `curve25519-dalek` and remove `RUSTSEC-2024-0344`"

This reverts commit a2a33b32e04681c10fe859f24ea0f0191fbcbde0.

## Patch
### Cargo.lock
```diff
@@ -1360,15 +1360,16 @@ dependencies = [
 
 [[package]]
 name = "curve25519-dalek"
-version = "4.1.3"
+version = "4.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "97fb8b7c4503de7d6ae7b42ab72a5a59857b4c937ec27a3d4539dba95b5ab2be"
+checksum = "f711ade317dd348950a9910f81c5947e3d8907ebd2b83f76203ff1807e6a2bc2"
 dependencies = [
  "cfg-if 1.0.0",
  "cpufeatures",
  "curve25519-dalek-derive",
  "digest 0.10.7",
  "fiat-crypto",
+ "platforms",
  "rustc_version",
  "subtle",
  "zeroize",
@@ -2003,9 +2004,9 @@ dependencies = [
 
 [[package]]
 name = "fiat-crypto"
-version = "0.2.9"
+version = "0.1.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "28dea519a9695b9977216879a3ebfddf92f1c08c05d984f8996aecd6ecdc811d"
+checksum = "e825f6987101665dea6ec934c09ec6d721de7bc1bf92248e1d5810c8cd636b77"
 
 [[package]]
 name = "filesize"
@@ -4194,6 +4195,12 @@ version = "0.3.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "26072860ba924cbfa98ea39c8c19b4dd6a4a25423dbdf219c1eca91aa0cf6964"
 
+[[package]]
+name = "platforms"
+version = "3.0.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e3d7ddaed09e0eb771a79ab0fd64609ba0afb0a8366421957936ad14cbd13630"
+
 [[package]]
 name = "plotters"
 version = "0.3.5"
```

### Makefile
```diff
@@ -145,7 +145,7 @@ lint-smart-contracts:
 
 .PHONY: audit-rs
 audit-rs:
-	$(CARGO) audit
+	$(CARGO) audit --ignore RUSTSEC-2024-0344
 
 .PHONY: audit-as
 audit-as:
```
