# [?] Fix postgres DoS advisories (RUSTSEC-2026-0178/0179/0180) (#26968)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-06-15
Source: https://github.com/MystenLabs/sui/commit/14c59d81505b738529ab7013b21cc2341adce79d
Type: security-commit

## Details
Fix postgres DoS advisories (RUSTSEC-2026-0178/0179/0180) (#26968)

## Summary

Three `vulnerability`-class advisories (published Jun 12) are currently
failing `cargo-deny advisories` on `main`, so every rust-touching PR
shows red. All are in the transitive postgres stack and have patched
releases:

| Advisory | Crate | Fix |
|---|---|---|
| RUSTSEC-2026-0179 | `postgres-protocol` 0.6.7 → **0.6.12** | SCRAM
CPU-exhaustion DoS |
| RUSTSEC-2026-0180 | `postgres-protocol` 0.6.7 → **0.6.12** | `hstore`
panic DoS |
| RUSTSEC-2026-0178 | `tokio-postgres` 0.7.12 → **0.7.18** | `DataRow`
panic DoS |

These come in via `tokio-postgres → bb8-postgres → sui-rpc-benchmark`
(and `sui-pg-db`) — tooling/benchmark crates, not the node binary; the
DoS vector is a malicious postgres *server* attacking the client. Still
real, and `cargo-deny` hard-fails, so this gets `main` green again.

**Lockfile-only — no workspace manifest changes.** The workspace already
declares `tokio-postgres = "0.7.12"` (caret), which permits 0.7.18.

### Why the delta is more than 3 lines

`tokio-postgres 0.7.18` requires `whoami 2.x`, which needs `libredox
>=0.1.12`; the lock had `libredox 0.1.4` pinned (via `filetime ← notify
← sui-data-ingestion-core`). A single-package `--precise` bump can't
move `libredox`, which is what blocked the naive update. Lifting
`libredox` to 0.1.17 (satisfies both `filetime`'s `^0.1.0` and
`whoami`'s `^0.1.12`) unblocks it, pulling these within-range transitive
bumps:

| Crate | Change | Reason |
|---|---|---|
| postgres-protocol | 0.6.7 → 0.6.12 | the fix |
| tokio-postgres | 0.7.12 → 0.7.18 | the fix |
| postgres-types | 0.2.8 → 0.2.14 | postgres stack |
| whoami | 1.5.0 → 2.1.0 | required by tokio-postgres 0.7.18 |
| libredox | 0.1.4 → 0.1.17 | required by whoami 2.x |
| redox_syscall | 0.5.13 → 0.8.1 | libredox dep |
| wasite | 0.1.0 → 1.0.2 | whoami 2.x dep |
| web-sys | 0.3.64 → 0.3.77 | whoami 2.x (wasm) |
| typenum | 1.16.0 → 1.20.1 | postgres-protocol 0.6.12 crypto deps |

All transitive support crates — no core sui crate changed.

## Test plan

- [x] `cargo deny check advisories` → **`advisories ok`** (was FAILED
with the 3 RUSTSEC IDs)
- [x] `cargo deny check bans licenses sources` → `bans ok, licenses ok,
sources ok` (no regression from the cascade)
- [x] `cargo metadata --locked` resolves (lockfile internally
consistent)
- [x] `cargo check --locked -p sui-pg-db -p sui-rpc-benchmark` →
compiles clean (the two crates that use tokio-postgres; 0.7.x/0.6.x
bumps are API-compatible)
- [x] external-crates (Move) workspace advisories already clean —
unaffected

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol:
- [ ] Nodes (Validators and Full nodes):
- [ ] gRPC:
- [ ] JSON-RPC:
- [ ] GraphQL:
- [ ] CLI:
- [ ] Rust SDK:
- [ ] Indexing Framework:

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

### Cargo.lock
```diff
@@ -50,7 +50,7 @@ version = "0.5.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5c192eb8f11fc081b0fe4259ba5af04217d4e0faddd02417310a927911abd7c8"
 dependencies = [
- "crypto-common",
+ "crypto-common 0.1.6",
  "generic-array",
 ]
 
@@ -2156,7 +2156,7 @@ dependencies = [
  "bytes",
  "form_urlencoded",
  "hex",
- "hmac",
+ "hmac 0.12.1",
  "http 0.2.9",
  "http 1.3.1",
  "percent-encoding",
@@ -2815,7 +2815,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b30ed1d6f8437a487a266c8293aeb95b61a23261273e3e02912cdb8b68bf798b"
 dependencies = [
  "bs58 0.4.0",
- "hmac",
+ "hmac 0.12.1",
  "k256 0.11.6",
  "once_cell",
  "pbkdf2",
@@ -2982,6 +2982,15 @@ dependencies = [
  "generic-array",
 ]
 
+[[package]]
+name = "block-buffer"
+version = "0.12.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d2f6c7dbe95a6ed67ad9f18e57daf93a2f034c524b99fd2b76d18fdfeb6660aa"
+dependencies = [
+ "hybrid-array",
+]
+
 [[package]]
 name = "block-padding"
 version = "0.2.1"
@@ -3473,7 +3482,7 @@ version = "0.4.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "773f3b9af64447d2ce9850330c473515014aa235e6a783b02db81ff39e4a3dad"
 dependencies = [
- "crypto-common",
+ "crypto-common 0.1.6",
  "inout",
 ]
 
@@ -3565,6 +3574,12 @@ dependencies = [
  "cc",
 ]
 
+[[package]]
+name = "cmov"
+version = "0.5.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "0c9ea0ac24bc397ab3c98583a3c9ba74fa56b09a4449bbe172b9b1ddb016027a"
+
 [[package]]
 name = "cmp_any"
 version = "0.8.1"
@@ -3840,6 +3855,12 @@ version = "0.9.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "520fbf3c07483f94e3e3ca9d0cfd913d7718ef2483d2cfd91c0d9e91474ab913"
 
+[[package]]
+name = "const-oid"
+version = "0.10.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a6ef517f0926dd24a1582492c791b6a4818a4d94e789a334894aa15b0d12f55c"
+
 [[package]]
 name = "const-random"
 version = "0.1.18"
@@ -4181,14 +4202,23 @@ dependencies = [
  "typenum",
 ]
 
+[[package]]
+name = "crypto-common"
+version = "0.2.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ce6e4c961d6cd6c9a86db418387425e8bdeaf05b3c8bc1411e6dca4c252f1453"
+dependencies = [
+ "hybrid-array",
+]
+
 [[package]]
 name = "csscolorparser"
 version = "0.6.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "eb2a7d3066da2de787b7f032c736763eb7ae5d355f81a68bab2675a96008b0bf"
 dependencies = [
  "lab",
- "phf",
+ "phf 0.11.1",
 ]
 
 [[package]]
@@ -4231,6 +4261,15 @@ dependencies = [
  "cipher",
 ]
 
+[[package]]
+name = "ctutils"
+version = "0.4.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7d5515a3834141de9eafb9717ad39eea8247b5674e6066c404e8c4b365d2a29e"
+dependencies = [
+ "cmov",
+]
+
 [[package]]
 name = "curve25519-dalek"
 version = "4.1.3"
@@ -4611,7 +4650,7 @@ version = "0.6.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f1a467a65c5e759bce6e65eaf91cc29f466cdc57cb65777bd646872a8a1fd4de"
 dependencies = [
- "const-oid",
+ "const-oid 0.9.2",
 ]
 
 [[package]]
@@ -4620,7 +4659,7 @@ version = "0.7.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f55bf8e7b65898637379c1b74eb1551107c8294ed26d855ceb9fd1a09cfc9bc0"
 dependencies = [
- "const-oid",
+ "const-oid 0.9.2",
  "pem-rfc7468",
  "zeroize",
 ]
@@ -4877,11 +4916,23 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9ed9a281f7bc9b7576e61468ba615a66a5c8cfdff42420a70aa82701a3b1e292"
 dependencies = [
  "block-buffer 0.10.3",
- "const-oid",
- "crypto-common",
+ "const-oid 0.9.2",
+ "crypto-common 0.1.6",
  "subtle",
 ]
 
+[[package]]
+name = "digest"
+version = "0.11.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f1dd6dbb5841937940781866fa1281a1ff7bd3bf827091440879f9994983d5c2"
+dependencies = [
+ "block-buffer 0.12.1",
+ "const-oid 0.10.2",
+ "crypto-common 0.2.2",
+ "ctutils",
+]
+
 [[package]]
 name = "dirs"
 version = "4.0.0"
@@ -6573,7 +6624,7 @@ version = "0.12.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7b5f8eb2ad728638ea2c7d47a21db23b7b58a72ed6a38256b8a1849f15fbbdf7"
 dependencies = [
- "hmac",
+ "hmac 0.12.1",
 ]
 
 [[package]]
@@ -6585,6 +6636,15 @@ dependencies = [
  "digest 0.10.7",
 ]
 
+[[package]]
+name = "hmac"
+version = "0.13.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "6303bc9732ae41b04cb554b844a762b4115a61bfaa81e3e83050991eeb56863f"
+dependencies = [
+ "digest 0.11.3",
+]
+
 [[package]]
 name = "hmac-sha512"
 version = "0.1.9"
@@ -6701,6 +6761,15 @@ version = "2.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9a3a5bfb195931eeb336b2a7b4d761daec841b97f947d34394601737a7bba5e4"
 
+[[package]]
+name = "hybrid-array"
+version = "0.4.12"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9155a582abd142abc056962c29e3ce5ff2ad5469f4246b537ed42c5deba857da"
+dependencies = [
+ "typenum",
+]
+
 [[package]]
 name = "hyper"
 version = "0.14.26"
@@ -7861,13 +7930,14 @@ dependencies = [
 
 [[package]]
 name = "libredox"
-version = "0.1.4"
+version = "0.1.17"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1580801010e535496706ba011c15f8532df6b42297d2e471fec38ceadd8c0638"
+checksum = "f02ab6bace2054fb888a3c16f990117b579d14a3088e472d63c6011fa185c9d3"
 dependencies = [
  "bitflags 2.11.0",
  "libc",
- "redox_syscall 0.5.13",
+ "plain",
+ "redox_syscall 0.8.1",
 ]
 
 [[package]]
@@ -8273,6 +8343,16 @@ dependencies = [
  "digest 0.10.7",
 ]
 
+[[package]]
+name = "md-5"
+version = "0.11.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "69b6441f590336821bb897fb28fc622898ccceb1d6cea3fde5ea86b090c4de98"
+dependencies = [
+ "cfg-if",
+ "digest 0.11.3",
+]
+
 [[package]]
 name = "memchr"
 version = "2.7.4"
@@ -9201,7 +9281,7 @@ dependencies = [
 name = "move-symbol-pool"
 version = "0.1.0"
 dependencies = [
- "phf",
+ "phf 0.11.1",
  "serde",
 ]
 
@@ -9852,7 +9932,7 @@ version = "0.50.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7957b9740744892f114936ab4a57b3f487491bbeafaf8083688b16841a4240e5"
 dependencies = [
- "windows-sys 0.61.2",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -10133,7 +10213,7 @@ dependencies = [
  "humantime",
  "hyper 1.8.1",
  "itertools 0.14.0",
- "md-5",
+ "md-5 0.10.6",
  "parking_lot 0.12.3",
  "percent-encoding",
  "quick-xml",
@@ -10170,7 +10250,7 @@ dependencies = [
  "humantime",
  "hyper 1.8.1",
  "itertools 0.14.0",
- "md-5",
+ "md-5 0.10.6",
  "parking_lot 0.12.3",
  "percent-encoding",
  "quick-xml",
@@ -10640,7 +10720,7 @@ dependencies = [
  "coset",
  "data-encoding",
  "getrandom 0.2.15",
- "hmac",
+ "hmac 0.12.1",
  "indexmap 2.8.0",
  "rand 0.8.5",
  "serde",
@@ -10829,6 +10909,16 @@ dependencies = [
  "phf_shared 0.11.1",
 ]
 
+[[package]]
+name = "phf"
+version = "0.13.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c1562dc717473dbaa4c1f85a36410e03c047b2e7df7f45ee938fbef64ae7fadf"
+dependencies = [
+ "phf_shared 0.13.1",
+ "serde",
+]
+
 [[package]]
 name = "phf_codegen"
 version = "0.11.3"
@@ -10880,6 +10970,15 @@ dependencies = [
  "siphasher 0.3.10",
 ]
 
+[[package]]
+name = "phf_shared"
+version = "0.13.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e57fef6bc5981e38c2ce2d63bfa546861309f875b8a75f092d1d54ae2d64f266"
+dependencies = [
+ "siphasher 1.0.1",
+]
+
 [[package]]
 name = "pin-project"
 version = "1.1.10"
@@ -10939,6 +11038,12 @@ version = "0.3.26"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6ac9a59f73473f1b8d852421e59e64809f025994837ef743615c6d0c5b305160"
 
+[[package]]
+name = "plain"
+version = "0.2.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "b4596b6d070b27117e987119b4dac604f3c58cfb0b191112e24771b2faeac1a6"
+
 [[package]]
 name = "plotters"
 version = "0.3.4"
@@ -10987,27 +11092,27 @@ checksum = "c33a9471896f1c69cecef8d20cbe2f7accd12527ce60845ff44c153bb2a21b49"
 
 [[package]]
 name = "postgres-protocol"
-version = "0.6.7"
+version = "0.6.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "acda0ebdebc28befa84bee35e651e4c5f09073d668c7aed4cf7e23c3cda84b23"
+checksum = "08808e3c483c46e999108051c78334f473d5adb59d78bb80a1268c7e6aa6c514"
 dependencies = [
  "base64 0.22.1",
  "byteorder",
  "bytes",
  "fallible-iterator",
- "hmac",
- "md-5",
+ "hmac 0.13.0",
+ "md-5 0.11.0",
  "memchr",
- "rand 0.8.5",
- "sha2 0.10.9",
+ "rand 0.10.0",
+ "sha2 0.11.0",
  "stringprep",
 ]
 
 [[package]]
 name = "postgres-types"
-version = "0.2.8"
+version = "0.2.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f66ea23a2d0e5734297357705193335e0a957696f34bed2f2faefacb2fec336f"
+checksum = "851ca9db4932932d69f3ea811b1abe63087a0f740a47692619dd40d4899b68be"
 dependencies = [
  "bytes",
  "fallible-iterator",
@@ -11332,7 +11437,7 @@ version = "0.14.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ac6c3320f9abac597dcbc668774ef006702672474aad53c6d596b62e487b40b1"
 dependencies = [
- "heck 0.5.0",
+ "heck 0.4.1",
  "itertools 0.14.0",
  "log",
  "multimap",
@@ -11974,9 +12079,9 @@ dependencies = [
 
 [[package]]
 name = "redox_syscall"
-version = "0.5.13"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0d04b7d0ee6b4a0207a0a7adb104d23ecb0b47d6beae7152d0fa34b692b29fd6"
+checksum = "5b44b894f2a6e36457d665d1e08c3866add6ed5e70050c1b4ba8a8ddedb02ce7"
 dependencies = [
  "bitflags 2.11.0",
 ]
@@ -12162,7 +12267,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7743f17af12fa0b03b803ba12cd6a8d9483a587e89c69445e3909655c0b9fabb"
 dependencies = [
  "crypto-bigint 0.4.9",
- "hmac",
+ "hmac 0.12.1",
  "zeroize",
 ]
 
@@ -12172,7 +12277,7 @@ version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f8dd2a808d456c4a54e300a23e9f5a67e122c3024119acbfd73e3bf664491cb2"
 dependencies = [
- "hmac",
+ "hmac 0.12.1",
  "subtle",
 ]
 
@@ -12296,7 +12401,7 @@ version = "0.9.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b8573f03f5883dcaebdfcf4725caa1ecb9c15b2ef50c43a07b816e06799bb12d"
 dependencies = [
- "const-oid",
+ "const-oid 0.9.2",
  "digest 0.10.7",
  "num-bigint-dig",
  "num-integer",
@@ -13146,6 +13251,17 @@ dependencies = [
  "digest 0.10.7",
 ]
 
+[[package]]
+name = "sha2"
+version = "0.11.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "446ba717509524cb3f22f17ecc096f10f4822d76ab5c0b9822c5f9c284e825f4"
+dependencies = [
+ "cfg-if",
+ "cpufeatures 0.3.0",
+ "digest 0.11.3",
+]
+
 [[package]]
 name = "sha3"
 version = "0.9.1"
@@ -16643,7 +16759,7 @@ dependencies = [
  "dashmap 5.5.3",
  "futures",
  "parking_lot 0.12.3",
- "phf",
+ "phf 0.11.1",
  "rand 0.8.5",
  "reqwest",
  "serde",
@@ -17734,7 +17850,7 @@ checksum = "d4ea810f0692f9f51b382fff5893887bb4580f5fa246fde546e0b13e7fcee662"
 dependencies = [
  "fnv",
  "nom 7.1.3",
- "phf",
+ "phf 0.11.1",
  "phf_codegen",
 ]
 
@@ -17777,7 +17893,7 @@ dependencies = [
  "ordered-float 4.6.0",
  "pest",
  "pest_derive",
- "phf",
+ "phf 0.11.1",
  "sha2 0.10.9",
  "signal-hook",
  "siphasher 1.0.1",
@@ -18106,7 +18222,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "62cc94d358b5a1e84a5cb9109f559aa3c4d634d2b1b4de3d0fa4adc7c78e2861"
 dependencies = [
  "anyhow",
- "hmac",
+ "hmac 0.12.1",
  "once_cell",
  "pbkdf2",
  "rand 0.8.5",
@@ -18208,9 +18324,9 @@ dependencies = [
 
 [[package]]
 name = "tokio-postgres"
-version = "0.7.12"
+version = "0.7.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3b5d3742945bc7d7f210693b0c58ae542c6fd47b17adbbda0885f3dcb34a6bdb"
+checksum = "a528f7d280f6d5b9cd149635c8705b0dd049754bc67d81d31fa25169a93809d3"
 dependencies = [
  "async-trait",
  "byteorder",
@@ -18221,12 +18337,12 @@ dependencies = [
  "log",
  "parking_lot 0.12.3",
  "percent-encoding",
- "phf",
+ "phf 0.13.1",
  "pin-project-lite",
  "postgres-protocol",
  "postgres-types",
- "rand 0.8.5",
- "socket2 0.5.6",
+ "rand 0.10.0",
+ "socket2 0.6.3",
  "tokio",
  "tokio-util 0.7.18 (registry+https://github.com/rust-lang/crates.io-index)",
  "whoami",
@@ -18942,7 +19058,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "97fee6b57c6a41524a810daee9286c02d7752c4253064d0b05472833a438f675"
 dependencies = [
  "cfg-if",
- "rand 0.8.5",
+ "rand 0.7.3",
  "static_assertions",
 ]
 
@@ -19027,9 +19143,9 @@ checksum = "0e13db2e0ccd5e14a544e8a246ba2312cd25223f616442d7f2cb0e3db614236e"
 
 [[package]]
 name = "typenum"
-version = "1.16.0"
+version = "1.20.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "497961ef93d974e23eb6f433eb5fe1b7930b659f06d12dec6fc44a8f554c0bba"
+checksum = "b6f5e870be6c3b371b77fe0ee0bafb859fa4964b4404c27de1d380043c4dda20"
 
 [[package]]
 name = "typeshare"
@@ -19184,7 +19300,7 @@ version = "0.5.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fc1de2c688dc15305988b563c3854064043356019f97a4b46276fe734c4f07ea"
 dependencies = [
- "crypto-common",
+ "crypto-common 0.1.6",
  "subtle",
 ]
 
@@ -19463,9 +19579,12 @@ dependencies = [
 
 [[package]]
 name = "wasite"
-version = "0.1.0"
+version = "1.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b8dad83b4f25e74f184f64c43b150b91efe7647395b42289f38e50566d82855b"
+checksum = "66fe902b4a6b8028a753d5424909b764ccf79b7a209eac9bf97e59cda9f71a42"
+dependencies = [
+ "wasi 0.14.2+wasi-0.2.4",
+]
 
 [[package]]
 name = "wasm-bindgen"
@@ -19615,9 +19734,9 @@ dependencies = [
 
 [[package]]
 name = "web-sys"
-version = "0.3.64"
+version = "0.3.77"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9b85cbef8c220a6abc02aefd892dfc0fc23afb1c6a426316ec33253a3877249b"
+checksum = "33b6dd2ef9186f1f2072e409e99cd22a975331a6b3591b12c764e0e55c60d5d2"
 dependencies = [
  "js-sys",
  "wasm-bindgen",
@@ -19743,11 +19862,11 @@ dependencies = [
 
 [[package]]
 name = "whoami"
-version = "1.5.0"
+version = "2.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0fec781d48b41f8163426ed18e8fc2864c12937df9ce54c88ede7bd47270893e"
+checksum = "8fae98cf96deed1b7572272dfc777713c249ae40aa1cf8862e091e8b745f5361"
 dependencies = [
- "redox_syscall 0.4.1",
+ "libredox",
  "wasite",
  "web-sys",
 ]
```
