# [?] Address cargo audit failure `RUSTSEC-2025-0009` (#7086)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-03-10
Source: https://github.com/sigp/lighthouse/commit/0f5e6801499bf230d249e851b639b58dac5dcccc
Type: security-commit

## Details
Address cargo audit failure `RUSTSEC-2025-0009` (#7086)

## Patch
### Cargo.lock
```diff
@@ -1963,7 +1963,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1145d32e826a7748b69ee8fc62d3e6355ff7f1051df53141e7048162fc90481b"
 dependencies = [
  "data-encoding",
- "syn 1.0.109",
+ "syn 2.0.98",
 ]
 
 [[package]]
@@ -2656,7 +2656,7 @@ dependencies = [
  "bls",
  "hex",
  "num-bigint-dig",
- "ring 0.16.20",
+ "ring",
  "sha2 0.9.9",
  "zeroize",
 ]
@@ -2828,7 +2828,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c853bd72c9e5787f8aafc3df2907c2ed03cff3150c3acd94e2e53a98ab70a8ab"
 dependencies = [
  "cpufeatures",
- "ring 0.17.8",
+ "ring",
  "sha2 0.10.8",
 ]
 
@@ -4713,7 +4713,7 @@ dependencies = [
  "base64 0.21.7",
  "js-sys",
  "pem",
- "ring 0.17.8",
+ "ring",
  "serde",
  "serde_json",
  "simple_asn1",
@@ -4800,7 +4800,7 @@ version = "1.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bbd2bcb4c963f2ddae06a2efc7e9f3591312473c50c6685e1f298068316e66fe"
 dependencies = [
- "spin 0.9.8",
+ "spin",
 ]
 
 [[package]]
@@ -5176,7 +5176,7 @@ dependencies = [
  "libp2p-tls",
  "quinn",
  "rand 0.8.5",
- "ring 0.17.8",
+ "ring",
  "rustls 0.23.22",
  "socket2",
  "thiserror 2.0.11",
@@ -5237,16 +5237,16 @@ dependencies = [
 
 [[package]]
 name = "libp2p-tls"
-version = "0.6.0"
+version = "0.6.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dcaebc1069dea12c5b86a597eaaddae0317c2c2cb9ec99dc94f82fd340f5c78b"
+checksum = "42bbf5084fb44133267ad4caaa72a253d68d709edd2ed1cf9b42431a8ead8fd5"
 dependencies = [
  "futures",
  "futures-rustls",
  "libp2p-core",
  "libp2p-identity",
  "rcgen",
- "ring 0.17.8",
+ "ring",
  "rustls 0.23.22",
  "rustls-webpki 0.101.7",
  "thiserror 2.0.11",
@@ -7116,7 +7116,7 @@ dependencies = [
  "bytes",
  "getrandom 0.2.15",
  "rand 0.8.5",
- "ring 0.17.8",
+ "ring",
  "rustc-hash 2.1.0",
  "rustls 0.23.22",
  "rustls-pki-types",
@@ -7276,12 +7276,13 @@ dependencies = [
 
 [[package]]
 name = "rcgen"
-version = "0.11.3"
+version = "0.13.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "52c4f3084aa3bc7dfbba4eff4fab2a54db4324965d8872ab933565e6fbd83bc6"
+checksum = "75e669e5202259b5314d1ea5397316ad400819437857b90861765f24c4cf80a2"
 dependencies = [
  "pem",
- "ring 0.16.20",
+ "ring",
+ "rustls-pki-types",
  "time",
  "yasna",
 ]
@@ -7463,31 +7464,15 @@ dependencies = [
 
 [[package]]
 name = "ring"
-version = "0.16.20"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3053cf52e236a3ed746dfc745aa9cacf1b791d846bdaf412f60a8d7d6e17c8fc"
-dependencies = [
- "cc",
- "libc",
- "once_cell",
- "spin 0.5.2",
- "untrusted 0.7.1",
- "web-sys",
- "winapi",
-]
-
-[[package]]
-name = "ring"
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
- "untrusted 0.9.0",
+ "untrusted",
  "windows-sys 0.52.0",
 ]
 
@@ -7701,7 +7686,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3f56a14d1f48b391359b22f731fd4bd7e43c97f3c50eee276f3aa09c94784d3e"
 dependencies = [
  "log",
- "ring 0.17.8",
+ "ring",
  "rustls-webpki 0.101.7",
  "sct",
 ]
@@ -7713,7 +7698,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bf4ef73721ac7bcd79b2b315da7779d8fc09718c6b3d2d1b2d94850eb8c18432"
 dependencies = [
  "log",
- "ring 0.17.8",
+ "ring",
  "rustls-pki-types",
  "rustls-webpki 0.102.8",
  "subtle",
@@ -7727,7 +7712,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9fb9263ab4eb695e42321db096e3b8fbd715a59b154d5c88d82db2175b681ba7"
 dependencies = [
  "once_cell",
- "ring 0.17.8",
+ "ring",
  "rustls-pki-types",
  "rustls-webpki 0.102.8",
  "subtle",
@@ -7767,8 +7752,8 @@ version = "0.101.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8b6275d1ee7a1cd780b64aca7726599a1dbc893b1e64144529e55c3c2f745765"
 dependencies = [
- "ring 0.17.8",
- "untrusted 0.9.0",
+ "ring",
+ "untrusted",
 ]
 
 [[package]]
@@ -7777,9 +7762,9 @@ version = "0.102.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "64ca1bc8749bd4cf37b5ce386cc146580777b4e8572c7b97baf22c83f444bee9"
 dependencies = [
- "ring 0.17.8",
+ "ring",
  "rustls-pki-types",
- "untrusted 0.9.0",
+ "untrusted",
 ]
 
 [[package]]
@@ -7911,8 +7896,8 @@ version = "0.7.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "da046153aa2352493d6cb7da4b6e5c0c057d8a1d0a9aa8560baffdd945acd414"
 dependencies = [
- "ring 0.17.8",
- "untrusted 0.9.0",
+ "ring",
+ "untrusted",
 ]
 
 [[package]]
@@ -8515,7 +8500,7 @@ dependencies = [
  "chacha20poly1305",
  "curve25519-dalek",
  "rand_core 0.6.4",
- "ring 0.17.8",
+ "ring",
  "rustc_version 0.4.1",
  "sha2 0.10.8",
  "subtle",
@@ -8531,12 +8516,6 @@ dependencies = [
  "windows-sys 0.52.0",
 ]
 
-[[package]]
-name = "spin"
-version = "0.5.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6e63cff320ae2c57904679ba7cb63280a3dc4613885beafb148ee7bf9aa9042d"
-
 [[package]]
 name = "spin"
 version = "0.9.8"
@@ -9700,12 +9679,6 @@ dependencies = [
  "tokio-util",
 ]
 
-[[package]]
-name = "untrusted"
-version = "0.7.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a156c684c91ea7d62626509bce3cb4e1d9ed5c4d978f7b4352658f96a4c26b4a"
-
 [[package]]
 name = "untrusted"
 version = "0.9.0"
```

### Cargo.toml
```diff
@@ -176,7 +176,7 @@ reqwest = { version = "0.11", default-features = false, features = [
     "rustls-tls",
     "native-tls-vendored",
 ] }
-ring = "0.16"
+ring = "0.17"
 rpds = "0.11"
 rusqlite = { version = "0.28", features = ["bundled"] }
 serde = { version = "1", features = ["derive"] }
```

### Makefile
```diff
@@ -250,7 +250,7 @@ install-audit:
 	cargo install --force cargo-audit
 
 audit-CI:
-	cargo audit --ignore RUSTSEC-2025-0009 --ignore RUSTSEC-2024-0437
+	cargo audit --ignore RUSTSEC-2024-0437
 
 # Runs `cargo vendor` to make sure dependencies can be vendored for packaging, reproducibility and archival purpose.
 vendor:
```
