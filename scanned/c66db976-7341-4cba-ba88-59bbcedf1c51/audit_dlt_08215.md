# [?] ci: update openssl-src to 111.25 as per RUSTSEC-2023-0007 (#30173)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-02-07
Source: https://github.com/solana-labs/solana/commit/5494146413300f0c1f9ecc43743798910ff4da16
Type: security-commit

## Details
ci: update openssl-src to 111.25 as per RUSTSEC-2023-0007 (#30173)

## Patch
### Cargo.lock
```diff
@@ -3145,9 +3145,9 @@ checksum = "28988d872ab76095a6e6ac88d99b54fd267702734fd7ffe610ca27f533ddb95a"
 
 [[package]]
 name = "openssl-src"
-version = "111.22.0+1.1.1q"
+version = "111.25.0+1.1.1t"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f31f0d509d1c1ae9cada2f9539ff8f37933831fd5098879e482aa687d659853"
+checksum = "3173cd3626c43e3854b1b727422a276e568d9ec5fe8cec197822cf52cfb743d6"
 dependencies = [
  "cc",
 ]
```

### programs/sbf/Cargo.lock
```diff
@@ -2903,9 +2903,9 @@ checksum = "ff011a302c396a5197692431fc1948019154afc178baf7d8e37367442a4601cf"
 
 [[package]]
 name = "openssl-src"
-version = "111.22.0+1.1.1q"
+version = "111.25.0+1.1.1t"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f31f0d509d1c1ae9cada2f9539ff8f37933831fd5098879e482aa687d659853"
+checksum = "3173cd3626c43e3854b1b727422a276e568d9ec5fe8cec197822cf52cfb743d6"
 dependencies = [
  "cc",
 ]
```
