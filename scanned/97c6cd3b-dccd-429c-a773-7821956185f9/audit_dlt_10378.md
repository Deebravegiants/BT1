# [?] Upgrading `aws-lc-rs` and `aws-lc-sys` to resolve reported vulnerabilities (#2926)

## Summary
Severity: Unknown
Chain: Sovereign SDK
Component: Sovereign-Labs/sovereign-sdk
Published: 2026-05-28
Source: https://github.com/Sovereign-Labs/sovereign-sdk/commit/57e19bcd3b325b7304b2dfe4646462fd6102ef53
Type: security-commit

## Details
Upgrading `aws-lc-rs` and `aws-lc-sys` to resolve reported vulnerabilities (#2926)

## Patch
### Cargo.lock
```diff
@@ -1468,19 +1468,19 @@ dependencies = [
 
 [[package]]
 name = "aws-lc-rs"
-version = "1.16.1"
+version = "1.17.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "94bffc006df10ac2a68c83692d734a465f8ee6c5b384d8545a636f81d858f4bf"
+checksum = "5ec2f1fc3ec205783a5da9a7e6c1509cc69dedf09a1949e412c1e18469326d00"
 dependencies = [
  "aws-lc-sys",
  "zeroize",
 ]
 
 [[package]]
 name = "aws-lc-sys"
-version = "0.38.0"
+version = "0.41.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4321e568ed89bb5a7d291a7f37997c2c0df89809d7b6d12062c81ddb54aa782e"
+checksum = "1a2f9779ce85b93ab6170dd940ad0169b5766ff848247aff13bb788b832fe3f4"
 dependencies = [
  "cc",
  "cmake",
@@ -3525,7 +3525,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8d162beedaa69905488a8da94f5ac3edb4dd4788b732fadb7bd120b2625c1976"
 dependencies = [
  "data-encoding",
- "syn 2.0.117",
+ "syn 1.0.109",
 ]
 
 [[package]]
```
