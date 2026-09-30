# [?] Bump tracing-subscriber to resolve RUSTSEC-2025-0055

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2026-04-16
Source: https://github.com/casper-network/casper-node/commit/982b565d15e29c5308086863dcf503565e718600
Type: security-commit

## Details
Bump tracing-subscriber to resolve RUSTSEC-2025-0055

## Patch
### Cargo.lock
```diff
@@ -2571,7 +2571,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cea14ef9355e3beab063703aa9dab15afd25f0667c341310c1e5274bb1d0da18"
 dependencies = [
  "libc",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -3617,7 +3617,7 @@ checksum = "e04d7f318608d35d4b61ddd75cbdaee86b023ebe2bd5a66ee0915f0bf93095a9"
 dependencies = [
  "hermit-abi 0.5.1",
  "libc",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -3910,11 +3910,11 @@ checksum = "ffbee8634e0d45d258acb448e7eaab3fce7a0a467395d4d9f228e3c1f01fb2e4"
 
 [[package]]
 name = "matchers"
-version = "0.1.0"
+version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8263075bb86c5a1b1427b5ae862e8889656f126e9f77c484496e8b47cf5c5558"
+checksum = "d1525a2a28c7f4fa0fc98bb91ae755d1e2d1505079e05539e35bc876b5d65ae9"
 dependencies = [
- "regex-automata 0.1.10",
+ "regex-automata",
 ]
 
 [[package]]
@@ -4205,12 +4205,11 @@ dependencies = [
 
 [[package]]
 name = "nu-ansi-term"
-version = "0.46.0"
+version = "0.50.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "77a8165726e8236064dbb45459242600304b42a5ea24ee2948e18e023bf7ba84"
+checksum = "7957b9740744892f114936ab4a57b3f487491bbeafaf8083688b16841a4240e5"
 dependencies = [
- "overload",
- "winapi",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -4436,12 +4435,6 @@ dependencies = [
  "winapi",
 ]
 
-[[package]]
-name = "overload"
-version = "0.1.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b15813163c1d831bf4a13c3610c05c0d03b39feb07f7e09fa234dac9b15aaf39"
-
 [[package]]
 name = "overwrite-uref-content"
 version = "0.1.0"
@@ -4823,7 +4816,7 @@ dependencies = [
  "rand",
  "rand_chacha",
  "rand_xorshift",
- "regex-syntax 0.8.5",
+ "regex-syntax",
  "rusty-fork",
  "tempfile",
  "unarray",
@@ -5131,17 +5124,8 @@ checksum = "b544ef1b4eac5dc2db33ea63606ae9ffcfac26c1416a2806ae0bf5f56b201191"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-automata 0.4.9",
- "regex-syntax 0.8.5",
-]
-
-[[package]]
-name = "regex-automata"
-version = "0.1.10"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6c230d73fb8d8c1b9c0b3135c5142a8acee3a0558fb8db5cf1cb65f8d7862132"
-dependencies = [
- "regex-syntax 0.6.29",
+ "regex-automata",
+ "regex-syntax",
 ]
 
 [[package]]
@@ -5152,15 +5136,9 @@ checksum = "809e8dc61f6de73b46c85f4c96486310fe304c434cfa43669d7b40f711150908"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-syntax 0.8.5",
+ "regex-syntax",
 ]
 
-[[package]]
-name = "regex-syntax"
-version = "0.6.29"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f162c6dd7b008981e4d40210aca20b4bd0f9b60ca9271061b07f78537722f2e1"
-
 [[package]]
 name = "regex-syntax"
 version = "0.8.5"
@@ -5506,7 +5484,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -6258,7 +6236,7 @@ dependencies = [
  "getrandom 0.3.3",
  "once_cell",
  "rustix",
- "windows-sys 0.59.0",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -6618,9 +6596,9 @@ checksum = "8df9b6e13f2d32c91b9bd719c00d1958837bc7dec474d94952798cc8e69eeec3"
 
 [[package]]
 name = "tracing"
-version = "0.1.41"
+version = "0.1.44"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "784e0ac535deb450455cbfa28a6f0df145ea1bb7ae51b821cf5e7927fdcfbdd0"
+checksum = "63e71662fa4b2a2c3a26f570f037eb95bb1f85397f3cd8076caed2f026a6d100"
 dependencies = [
  "log",
  "pin-project-lite",
@@ -6630,9 +6608,9 @@ dependencies = [
 
 [[package]]
 name = "tracing-attributes"
-version = "0.1.28"
+version = "0.1.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "395ae124c09f9e6918a2310af6038fba074bcf474ac352496d5910dd59a2226d"
+checksum = "7490cfa5ec963746568740651ac6781f701c9c5ea257c58e057f3ba8cf69e8da"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -6641,9 +6619,9 @@ dependencies = [
 
 [[package]]
 name = "tracing-core"
-version = "0.1.33"
+version = "0.1.36"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e672c95779cf947c5311f83787af4fa8fffd12fb27e4993211a84bdfd9610f9c"
+checksum = "db97caf9d906fbde555dd62fa95ddba9eecfd14cb388e4f491a66d74cd5fb79a"
 dependencies = [
  "once_cell",
  "valuable",
@@ -6682,14 +6660,14 @@ dependencies = [
 
 [[package]]
 name = "tracing-subscriber"
-version = "0.3.19"
+version = "0.3.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e8189decb5ac0fa7bc8b96b7cb9b2701d60d48805aca84a238004d665fcc4008"
+checksum = "2054a14f5307d601f88daf0553e1cbf472acc4f2c51afab632431cdcd72124d5"
 dependencies = [
  "matchers",
  "nu-ansi-term",
  "once_cell",
- "regex",
+ "regex-automata",
  "serde",
  "serde_json",
  "sharded-slab",
@@ -6877,7 +6855,7 @@ version = "1.6.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "97fee6b57c6a41524a810daee9286c02d7752c4253064d0b05472833a438f675"
 dependencies = [
- "cfg-if 1.0.0",
+ "cfg-if 0.1.10",
  "static_assertions",
 ]
 
@@ -7696,7 +7674,7 @@ version = "0.1.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cf221c93e13a30d793f7645a0e7762c55d169dbb0a49671918a2319d289b10bb"
 dependencies = [
- "windows-sys 0.59.0",
+ "windows-sys 0.48.0",
 ]
 
 [[package]]
```

### Makefile
```diff
@@ -131,7 +131,7 @@ lint-smart-contracts:
 
 .PHONY: audit-rs
 audit-rs:
-	$(CARGO) audit --ignore RUSTSEC-2025-0055 --ignore RUSTSEC-2026-0001 --ignore RUSTSEC-2026-0007 --ignore RUSTSEC-2026-0049 --ignore RUSTSEC-2026-0068 --ignore RUSTSEC-2026-0067 --ignore RUSTSEC-2026-0098 --ignore RUSTSEC-2026-0099
+	$(CARGO) audit --ignore RUSTSEC-2026-0001 --ignore RUSTSEC-2026-0007 --ignore RUSTSEC-2026-0049 --ignore RUSTSEC-2026-0068 --ignore RUSTSEC-2026-0067 --ignore RUSTSEC-2026-0098 --ignore RUSTSEC-2026-0099
 
 .PHONY: audit
 audit: audit-rs
```

### node/Cargo.toml
```diff
@@ -88,7 +88,7 @@ toml = { version = "0.8.19", features = ["preserve_order"] }
 tower = { version = "0.4.6", features = ["limit"] }
 tracing = "0.1.18"
 tracing-futures = "0.2.5"
-tracing-subscriber = { version = "0.3.15", features = ["env-filter", "fmt", "json"] }
+tracing-subscriber = { version = "0.3.20", features = ["env-filter", "fmt", "json"] }
 uint = "0.9.0"
 uuid = { version = "0.8.1", features = ["serde", "v4"] }
 warp = { version = "0.3.6", features = ["compression"] }
```
