# [?] fix: address RUSTSEC-2025-0009 (#5710)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-03-07
Source: https://github.com/chainflip-io/chainflip-backend/commit/60f8614a485520fb705cb07c0f6027a0fb35944f
Type: security-commit

## Details
fix: address RUSTSEC-2025-0009 (#5710)

## Patch
### .cargo/config.toml
```diff
@@ -45,6 +45,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2024-0388: Unmaintained transitive dependency `derivative` used by substrate.
 # - RUSTSEC-2024-0384: Unmaintained transitive dependency `instant` used by substrate.
 # - RUSTSEC-2024-0421: Transitive dependency `idna` used by libp2p, among others.
+# - RUSTSEC-2025-0009: Transitive dependency use by rustls 0.20.9, as per the advisory, TLS is unaffected.
 cf-audit = '''
 audit -D unmaintained -D unsound
     --ignore RUSTSEC-2021-0139
@@ -58,4 +59,5 @@ audit -D unmaintained -D unsound
     --ignore RUSTSEC-2024-0388
     --ignore RUSTSEC-2024-0384
     --ignore RUSTSEC-2024-0421
+    --ignore RUSTSEC-2025-0009
 '''
```

### Cargo.lock
```diff
@@ -5725,15 +5725,6 @@ dependencies = [
  "either",
 ]
 
-[[package]]
-name = "itertools"
-version = "0.12.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ba291022dbbd398a455acf126c1e341954079855bc60dfdda641363bd6922569"
-dependencies = [
- "either",
-]
-
 [[package]]
 name = "itertools"
 version = "0.13.0"
@@ -9466,7 +9457,7 @@ checksum = "22505a5c94da8e3b7c2996394d1c933236c4d743e81a410bcca4e6989fc066a4"
 dependencies = [
  "bytes",
  "heck 0.5.0",
- "itertools 0.12.1",
+ "itertools 0.11.0",
  "log",
  "multimap 0.10.0",
  "once_cell",
@@ -9499,7 +9490,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "81bddcdb20abf9501610992b6759a4c888aef7d1a7247ef75e2404275ac24af1"
 dependencies = [
  "anyhow",
- "itertools 0.12.1",
+ "itertools 0.11.0",
  "proc-macro2",
  "quote",
  "syn 2.0.96",
@@ -10059,15 +10050,14 @@ dependencies = [
 
 [[package]]
 name = "ring"
-version = "0.17.8"
+version = "0.17.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c17fa4cb658e3583423e915b9f3acc01cceaee1860e33d59ebae66adc3a2dc0d"
+checksum = "70ac5d832aa16abd7d1def883a8545280c20a60f523a370aa3a9617c2b8550ee"
 dependencies = [
  "cc",
  "cfg-if",
  "getrandom 0.2.15",
  "libc",
- "spin 0.9.8",
  "untrusted 0.9.0",
  "windows-sys 0.52.0",
 ]
@@ -10266,7 +10256,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3f56a14d1f48b391359b22f731fd4bd7e43c97f3c50eee276f3aa09c94784d3e"
 dependencies = [
  "log",
- "ring 0.17.8",
+ "ring 0.17.13",
  "rustls-webpki 0.101.7",
  "sct",
 ]
@@ -10279,7 +10269,7 @@ checksum = "8f287924602bf649d949c63dc8ac8b235fa5387d394020705b80c4eb597ce5b8"
 dependencies = [
  "log",
  "once_cell",
- "ring 0.17.8",
+ "ring 0.17.13",
  "rustls-pki-types",
  "rustls-webpki 0.102.8",
  "subtle 2.6.1",
@@ -10368,7 +10358,7 @@ version = "0.101.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8b6275d1ee7a1cd780b64aca7726599a1dbc893b1e64144529e55c3c2f745765"
 dependencies = [
- "ring 0.17.8",
+ "ring 0.17.13",
  "untrusted 0.9.0",
 ]
 
@@ -10378,7 +10368,7 @@ version = "0.102.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "64ca1bc8749bd4cf37b5ce386cc146580777b4e8572c7b97baf22c83f444bee9"
 dependencies = [
- "ring 0.17.8",
+ "ring 0.17.13",
  "rustls-pki-types",
  "untrusted 0.9.0",
 ]
@@ -11791,7 +11781,7 @@ version = "0.7.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "da046153aa2352493d6cb7da4b6e5c0c057d8a1d0a9aa8560baffdd945acd414"
 dependencies = [
- "ring 0.17.8",
+ "ring 0.17.13",
  "untrusted 0.9.0",
 ]
 
@@ -12361,7 +12351,7 @@ dependencies = [
  "chacha20poly1305",
  "curve25519-dalek 4.1.3",
  "rand_core 0.6.4",
- "ring 0.17.8",
+ "ring 0.17.13",
  "rustc_version",
  "sha2 0.10.8",
  "subtle 2.6.1",
@@ -15713,7 +15703,7 @@ version = "0.22.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ed63aea5ce73d0ff405984102c42de94fc55a6b75765d621c65262469b3c9b53"
 dependencies = [
- "ring 0.17.8",
+ "ring 0.17.13",
  "untrusted 0.9.0",
 ]
 
```
