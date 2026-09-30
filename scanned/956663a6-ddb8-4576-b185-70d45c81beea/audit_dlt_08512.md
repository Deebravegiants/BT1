# [?] chore: upgrade lru to resolve `RUSTSEC-2026-0002` advisory (#14859)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-01-09
Source: https://github.com/near/nearcore/commit/3162a4a43415a7d2050085adcaf923fde79a5532
Type: security-commit

## Details
chore: upgrade lru to resolve `RUSTSEC-2026-0002` advisory (#14859)

Upgrades `lru` crate to 0.16.3 to fix
https://rustsec.org/advisories/RUSTSEC-2026-0002

## Patch
### Cargo.lock
```diff
@@ -2355,6 +2355,12 @@ version = "0.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f81ec6369c545a7d40e4589b5597581fa1c441fe1cce96dd1de43159910a36a2"
 
+[[package]]
+name = "foldhash"
+version = "0.2.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "77ce24cb58228fbb8aa041425bb1050850ac19177686ea6e0f41a70416f56fdb"
+
 [[package]]
 name = "foreign-types"
 version = "0.3.2"
@@ -2688,18 +2694,14 @@ name = "hashbrown"
 version = "0.14.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e5274423e17b7c9fc20b6e7e208532f9b19825d82dfd615708b70edd83df41f1"
-dependencies = [
- "ahash 0.8.11",
- "allocator-api2",
-]
 
 [[package]]
 name = "hashbrown"
 version = "0.15.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bf151400ff0baff5465007dd2f3e717f3fe502074ca563069ce3a6629d07b289"
 dependencies = [
- "foldhash",
+ "foldhash 0.1.3",
  "serde",
 ]
 
@@ -2708,6 +2710,11 @@ name = "hashbrown"
 version = "0.16.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "841d1cc9bed7f9236f321df977030373f4a4163ae1a7dbfe1a51a2c1a51d9100"
+dependencies = [
+ "allocator-api2",
+ "equivalent",
+ "foldhash 0.2.0",
+]
 
 [[package]]
 name = "hashlink"
@@ -3703,11 +3710,11 @@ dependencies = [
 
 [[package]]
 name = "lru"
-version = "0.12.3"
+version = "0.16.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d3262e75e648fce39813cb56ac41f3c3e3f65217ebf3844d818d1f9398cfb0dc"
+checksum = "a1dc47f592c06f33f8e3aea9591776ec7c9f9e4124778ff8a3c3b87159f7e593"
 dependencies = [
- "hashbrown 0.14.5",
+ "hashbrown 0.16.1",
 ]
 
 [[package]]
@@ -4063,7 +4070,7 @@ name = "near-cache"
 version = "0.0.0"
 dependencies = [
  "bencher",
- "lru 0.12.3",
+ "lru 0.16.3",
  "parking_lot 0.12.1",
  "rand 0.8.5",
 ]
@@ -4082,7 +4089,7 @@ dependencies = [
  "enum-map",
  "insta",
  "itertools 0.14.0",
- "lru 0.12.3",
+ "lru 0.16.3",
  "near-async",
  "near-cache",
  "near-chain-configs",
@@ -4162,7 +4169,7 @@ version = "0.0.0"
 dependencies = [
  "assert_matches",
  "itertools 0.14.0",
- "lru 0.12.3",
+ "lru 0.16.3",
  "near-async",
  "near-chain",
  "near-chain-configs",
@@ -4201,7 +4208,7 @@ dependencies = [
  "criterion",
  "futures",
  "itertools 0.14.0",
- "lru 0.12.3",
+ "lru 0.16.3",
  "near-async",
  "near-cache",
  "near-chain",
@@ -4675,7 +4682,7 @@ dependencies = [
  "futures-util",
  "im",
  "itertools 0.14.0",
- "lru 0.12.3",
+ "lru 0.16.3",
  "named-lock",
  "near-async",
  "near-chain-configs",
@@ -5010,7 +5017,7 @@ dependencies = [
  "insta",
  "itertools 0.14.0",
  "itoa",
- "lru 0.12.3",
+ "lru 0.16.3",
  "near-async",
  "near-chain",
  "near-chain-configs",
@@ -5218,7 +5225,7 @@ dependencies = [
  "finite-wasm 0.5.0",
  "finite-wasm 0.6.0",
  "hex",
- "lru 0.12.3",
+ "lru 0.16.3",
  "memoffset 0.8.0",
  "near-crypto",
  "near-o11y",
```

### Cargo.toml
```diff
@@ -221,7 +221,7 @@ itertools = "0.14.0"
 itoa = "1.0"
 json_comments = "0.2.1"
 libc = "0.2.81"
-lru = "0.12.3"
+lru = "0.16.3"
 memoffset = "0.8"
 merlin = { version = "3", default-features = false }
 more-asserts = "0.2"
```

### deny.toml
```diff
@@ -78,6 +78,10 @@ skip = [
     { name = "hashbrown", version = "0.15.2" },
     { name = "zerocopy", version = "^0.7" },
 
+    # foldhash
+    { name = "foldhash", version = "=0.2.0" },
+    { name = "foldhash", version = "=0.1.3" },
+
     # Bolero requires a newer version and the rest of the ecosystem hasn't caught up yet.
     { name = "bitflags", version = "=1.3.2" },
     { name = "indexmap", version = "=1.9.2" },
@@ -120,7 +124,7 @@ skip = [
     { name = "base64", version = "^0.21" },
 
     # okApi uses mostly schemars 0.8 for now, though it's not necessary
-    { name = "schemars" , version = "^0.8" },
+    { name = "schemars", version = "^0.8" },
     { name = "schemars_derive", version = "^0.8" },
 
     # Bolero depends on outdated versions of these
```
