# [?] chore: handle RUSTSEC-2026-0049 (#6502)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2026-03-24
Source: https://github.com/chainflip-io/chainflip-backend/commit/00dea5b6da630e325cde8e638881a81dfccc7f80
Type: security-commit

## Details
chore: handle RUSTSEC-2026-0049 (#6502)

## Patch
### .cargo/config.toml
```diff
@@ -59,6 +59,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2026-0009: Medium severity, but only exploitable if user-provided strings are parsed into a time format by the `time` dependency.
 # - RUSTSEC-2026-0020: Wasmtime memory leak, we don't have any control over the wasmtime version.
 # - RUSTSEC-2026-0021: Wasmtime panic, we don't have any control over the wasmtime version.
+# - RUSTSEC-2026-0049: Transitive dependency and "an attacker would need to compromise a trusted issuing authority to trigger this bug". It's a dependency of `rustls`.
 #
 cf-audit = '''
 audit -D unmaintained -D unsound
@@ -85,6 +86,7 @@ audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2026-0009
 	--ignore RUSTSEC-2026-0020
 	--ignore RUSTSEC-2026-0021
+	--ignore RUSTSEC-2026-0049
 '''
 
 [build]
```

### Cargo.lock
```diff
@@ -1395,7 +1395,7 @@ checksum = "d1da5ab77c1437701eeff7c88d968729e7766172279eab0676857b3d63af7a6f"
 dependencies = [
  "borsh-derive",
  "cfg_aliases 0.2.1",
- "hashbrown 0.15.5",
+ "hashbrown 0.12.3",
 ]
 
 [[package]]
@@ -4292,7 +4292,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"
 dependencies = [
  "libc",
- "windows-sys 0.61.2",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -6387,7 +6387,7 @@ dependencies = [
  "libc",
  "percent-encoding",
  "pin-project-lite",
- "socket2 0.6.2",
+ "socket2 0.5.10",
  "tokio",
  "tower-service",
  "tracing",
@@ -6806,7 +6806,7 @@ checksum = "3640c1c38b8e4e43584d8df18be5fc6b0aa314ce6ebf51b53313d4306cca8e46"
 dependencies = [
  "hermit-abi 0.5.2",
  "libc",
- "windows-sys 0.61.2",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -9963,7 +9963,7 @@ checksum = "4e69bf016dc406eff7d53a7d3f7cf1c2e72c82b9088aac1118591e36dd2cd3e9"
 dependencies = [
  "bitcoin_hashes 0.13.0",
  "rand 0.8.5",
- "rand_core 0.6.4",
+ "rand_core 0.5.1",
  "serde",
  "unicode-normalization",
 ]
@@ -11171,7 +11171,7 @@ version = "0.13.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "be769465445e8c1474e9c5dac2018218498557af32d9ed057325ec9a41ae81bf"
 dependencies = [
- "heck 0.5.0",
+ "heck 0.4.1",
  "itertools 0.14.0",
  "log",
  "multimap",
@@ -11332,7 +11332,7 @@ dependencies = [
  "quinn-udp",
  "rustc-hash 2.1.1",
  "rustls 0.23.37",
- "socket2 0.6.2",
+ "socket2 0.5.10",
  "thiserror 2.0.18",
  "tokio",
  "tracing",
@@ -11369,9 +11369,9 @@ dependencies = [
  "cfg_aliases 0.2.1",
  "libc",
  "once_cell",
- "socket2 0.6.2",
+ "socket2 0.5.10",
  "tracing",
- "windows-sys 0.60.2",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -12027,7 +12027,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.12.1",
- "windows-sys 0.61.2",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -12052,7 +12052,7 @@ dependencies = [
  "once_cell",
  "ring 0.17.14",
  "rustls-pki-types",
- "rustls-webpki 0.103.9",
+ "rustls-webpki 0.103.10",
  "subtle 2.6.1",
  "zeroize",
 ]
@@ -12102,7 +12102,7 @@ dependencies = [
  "rustls 0.23.37",
  "rustls-native-certs",
  "rustls-platform-verifier-android",
- "rustls-webpki 0.103.9",
+ "rustls-webpki 0.103.10",
  "security-framework",
  "security-framework-sys",
  "webpki-root-certs 0.26.11",
@@ -12127,9 +12127,9 @@ dependencies = [
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.9"
+version = "0.103.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d7df23109aa6c1567d1c575b9952556388da57401e4ace1d15f79eedad0d8f53"
+checksum = "df33b2b81ac578cabaf06b89b0631153a3f416b0a886e8a7a1707fb51abbd1ef"
 dependencies = [
  "ring 0.17.14",
  "rustls-pki-types",
@@ -16502,7 +16502,7 @@ dependencies = [
  "getrandom 0.4.1",
  "once_cell",
  "rustix 1.1.4",
- "windows-sys 0.61.2",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -18502,7 +18502,7 @@ version = "0.1.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c2a7b1c03c876122aa43f3020e6c3c3ee5c05081c9a00739faf7503aeba10d22"
 dependencies = [
- "windows-sys 0.61.2",
+ "windows-sys 0.48.0",
 ]
 
 [[package]]
```
