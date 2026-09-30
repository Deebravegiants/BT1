# [?] chore: ignore RUSTSEC-2025-0141 (#6349)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2026-01-08
Source: https://github.com/chainflip-io/chainflip-backend/commit/e0925114624dd0ff8f6fe9c1f4afb89864ac3295
Type: security-commit

## Details
chore: ignore RUSTSEC-2025-0141 (#6349)

* chore: ignore RUSTSEC-2025-0141

* chore: fix/ignore RUSTSEC-2026-0002

## Patch
### .cargo/config.toml
```diff
@@ -57,6 +57,8 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2025-0118: Unsound API access to a WebAssembly shared linear memory.
 # - RUSTSEC-2025-0120: Unmaintained JSON crate. Only used for config.
 # - RUSTSEC-2025-0134: Unmaintained rustls-pemfile crate (version 1.0.4 and 2.2.0). Substrate dependency.
+# - RUSTSEC-2025-0141: Unmaintained bincode crate. Wasmtime dependency.
+# - RUSTSEC-2026-0002: Unsoundness in the lru crate. Our immediate dependency is patched, but not the transitive dependency, which is limited to libp2p-identify and smoldot crates.
 cf-audit = '''
 audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2021-0139
@@ -82,6 +84,8 @@ audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2025-0118
 	--ignore RUSTSEC-2025-0120
 	--ignore RUSTSEC-2025-0134
+	--ignore RUSTSEC-2025-0141
+	--ignore RUSTSEC-2026-0002
 '''
 
 [build]
```

### Cargo.lock
```diff
@@ -2796,7 +2796,7 @@ dependencies = [
  "itertools 0.13.0",
  "jsonrpsee 0.23.2",
  "log",
- "lru 0.13.0",
+ "lru 0.16.3",
  "pallet-cf-elections",
  "pallet-cf-environment",
  "pallet-cf-funding",
@@ -3001,7 +3001,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8d162beedaa69905488a8da94f5ac3edb4dd4788b732fadb7bd120b2625c1976"
 dependencies = [
  "data-encoding",
- "syn 1.0.109",
+ "syn 2.0.110",
 ]
 
 [[package]]
@@ -3586,7 +3586,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"
 dependencies = [
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -5068,6 +5068,11 @@ name = "hashbrown"
 version = "0.16.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5419bdc4f6a9207fbeba6d11b604d481addf78ecd10c11ad51e76c2f6482748d"
+dependencies = [
+ "allocator-api2",
+ "equivalent",
+ "foldhash 0.2.0",
+]
 
 [[package]]
 name = "hashers"
@@ -5420,7 +5425,7 @@ dependencies = [
  "hyper 1.8.1",
  "libc",
  "pin-project-lite",
- "socket2 0.5.10",
+ "socket2 0.6.1",
  "tokio",
  "tower-service",
  "tracing",
@@ -5832,7 +5837,7 @@ checksum = "3640c1c38b8e4e43584d8df18be5fc6b0aa314ce6ebf51b53313d4306cca8e46"
 dependencies = [
  "hermit-abi 0.5.2",
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -7065,11 +7070,11 @@ dependencies = [
 
 [[package]]
 name = "lru"
-version = "0.13.0"
+version = "0.16.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "227748d55f2f0ab4735d87fd623798cb6b664512fe979705f829c9f81c934465"
+checksum = "a1dc47f592c06f33f8e3aea9591776ec7c9f9e4124778ff8a3c3b87159f7e593"
 dependencies = [
- "hashbrown 0.15.5",
+ "hashbrown 0.16.0",
 ]
 
 [[package]]
@@ -7851,7 +7856,7 @@ version = "0.50.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7957b9740744892f114936ab4a57b3f487491bbeafaf8083688b16841a4240e5"
 dependencies = [
- "windows-sys 0.60.2",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -8893,7 +8898,7 @@ checksum = "4e69bf016dc406eff7d53a7d3f7cf1c2e72c82b9088aac1118591e36dd2cd3e9"
 dependencies = [
  "bitcoin_hashes 0.13.0",
  "rand",
- "rand_core 0.5.1",
+ "rand_core 0.6.4",
  "serde",
  "unicode-normalization",
 ]
@@ -10567,7 +10572,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.4.15",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -10580,7 +10585,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.11.0",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -14608,7 +14613,7 @@ dependencies = [
  "getrandom 0.3.4",
  "once_cell",
  "rustix 1.1.2",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -16221,7 +16226,7 @@ version = "0.1.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c2a7b1c03c876122aa43f3020e6c3c3ee5c05081c9a00739faf7503aeba10d22"
 dependencies = [
- "windows-sys 0.48.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
```

### Cargo.toml
```diff
@@ -123,7 +123,7 @@ lazy_static = { version = "1.4" }
 libp2p-identity = { version = "0.2.3" }
 libsecp256k1 = { version = "0.7", default-features = false }
 log = { version = "0.4.16" }
-lru = { version = "0.13.0", default-features = false }
+lru = { version = "0.16.3", default-features = false }
 mockall = { version = "0.13.0" }
 nanorand = { version = "0.7.0", default-features = false }
 num-bigint = { version = "0.4.3" }
```
