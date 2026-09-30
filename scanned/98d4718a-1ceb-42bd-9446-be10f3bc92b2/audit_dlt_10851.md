# [?] [bcs] fix to_address panic bug (#2093)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2021-02-02
Source: https://github.com/starcoinorg/starcoin/commit/c24ca89dd3da689eca0afd23eea2e6ebeb811cc6
Type: security-commit

## Details
[bcs] fix to_address panic bug (#2093)

Co-authored-by: jolestar <jolestar@gmail.com>

## Patch
### Cargo.lock
```diff
@@ -3,7 +3,7 @@
 [[package]]
 name = "abigen"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "bcs",
@@ -861,7 +861,7 @@ dependencies = [
 [[package]]
 name = "boogie-backend"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "bytecode",
  "diem-types",
@@ -879,7 +879,7 @@ dependencies = [
 [[package]]
 name = "borrow-graph"
 version = "0.0.1"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
  "mirai-annotations",
@@ -930,7 +930,7 @@ checksum = "e3b5ca7a04898ad4bcd41c90c5285445ff5b791899bb1b0abdd2a2aa791211d7"
 [[package]]
 name = "bytecode"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "borrow-graph",
  "bytecode-verifier",
@@ -951,7 +951,7 @@ dependencies = [
 [[package]]
 name = "bytecode-source-map"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "bcs",
@@ -968,7 +968,7 @@ dependencies = [
 [[package]]
 name = "bytecode-verifier"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "borrow-graph",
@@ -1803,7 +1803,7 @@ checksum = "993a608597367c6377b258c25d7120740f00ed23a2252b729b1932dd7866f908"
 [[package]]
 name = "datatest-stable"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
  "regex",
@@ -1878,7 +1878,7 @@ dependencies = [
 [[package]]
 name = "diem-crypto"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "aes-gcm 0.8.0",
  "anyhow",
@@ -1912,7 +1912,7 @@ dependencies = [
 [[package]]
 name = "diem-crypto-derive"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
  "proc-macro2 1.0.24",
@@ -1923,15 +1923,15 @@ dependencies = [
 [[package]]
 name = "diem-infallible"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
 ]
 
 [[package]]
 name = "diem-log-derive"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
  "proc-macro2 1.0.24",
@@ -1942,7 +1942,7 @@ dependencies = [
 [[package]]
 name = "diem-logger"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "backtrace",
  "chrono",
@@ -1960,7 +1960,7 @@ dependencies = [
 [[package]]
 name = "diem-network-address"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "aes-gcm 0.8.0",
  "bcs",
@@ -1976,7 +1976,7 @@ dependencies = [
 [[package]]
 name = "diem-nibble"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
  "serde",
@@ -1985,7 +1985,7 @@ dependencies = [
 [[package]]
 name = "diem-proptest-helpers"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "crossbeam 0.8.0",
  "diem-workspace-hack",
@@ -1996,7 +1996,7 @@ dependencies = [
 [[package]]
 name = "diem-temppath"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
  "hex",
@@ -2006,7 +2006,7 @@ dependencies = [
 [[package]]
 name = "diem-types"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "bcs",
@@ -2033,7 +2033,7 @@ dependencies = [
 [[package]]
 name = "diem-workspace-hack"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "byteorder",
  "bytes 1.0.1",
@@ -2131,7 +2131,7 @@ dependencies = [
 [[package]]
 name = "docgen"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "bytecode",
@@ -2287,7 +2287,7 @@ dependencies = [
 [[package]]
 name = "errmapgen"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "bcs",
@@ -3401,7 +3401,7 @@ checksum = "47be2f14c678be2fdcab04ab1171db51b2762ce6f0a8ee87c8dd4a04ed216135"
 [[package]]
 name = "ir-to-bytecode"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "bytecode-source-map",
@@ -3420,7 +3420,7 @@ dependencies = [
 [[package]]
 name = "ir-to-bytecode-syntax"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "codespan",
@@ -4378,7 +4378,7 @@ checksum = "b48e78b8626927bd980dff38d8147006323f5d7634d7bc9e31c3a59e07da1b28"
 [[package]]
 name = "move-core-types"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "bcs",
@@ -4420,7 +4420,7 @@ dependencies = [
 [[package]]
 name = "move-ir-types"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "codespan",
@@ -4435,7 +4435,7 @@ dependencies = [
 [[package]]
 name = "move-lang"
 version = "0.0.1"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "bcs",
@@ -4463,7 +4463,7 @@ dependencies = [
 [[package]]
 name = "move-lang-test-utils"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "datatest-stable",
  "diem-workspace-hack",
@@ -4472,7 +4472,7 @@ dependencies = [
 [[package]]
 name = "move-model"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "bytecode-source-map",
@@ -4537,7 +4537,7 @@ dependencies = [
 [[package]]
 name = "move-prover-test-utils"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "diem-workspace-hack",
@@ -4548,7 +4548,7 @@ dependencies = [
 [[package]]
 name = "move-vm-natives"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-crypto",
  "diem-workspace-hack",
@@ -4563,7 +4563,7 @@ dependencies = [
 [[package]]
 name = "move-vm-runtime"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "bytecode-verifier",
  "diem-crypto",
@@ -4582,7 +4582,7 @@ dependencies = [
 [[package]]
 name = "move-vm-types"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "bcs",
  "diem-crypto",
@@ -4988,7 +4988,7 @@ dependencies = [
 [[package]]
 name = "num-variants"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
  "proc-macro2 1.0.24",
@@ -6901,7 +6901,7 @@ checksum = "7fdf1b9db47230893d76faad238fd6097fd6d6a9245cd7a4d90dbd639536bbd2"
 [[package]]
 name = "short-hex-str"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
  "mirai-annotations",
@@ -9994,7 +9994,7 @@ checksum = "b5a972e5669d67ba988ce3dc826706fb0a8b01471c088cb0b6110b805cc36aed"
 [[package]]
 name = "vm"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "diem-crypto",
@@ -10331,7 +10331,7 @@ checksum = "85e60b0d1b5f99db2556934e21937020776a5d31520bf169e851ac44e6420214"
 [[package]]
 name = "x"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "anyhow",
  "chrono",
@@ -10357,7 +10357,7 @@ dependencies = [
 [[package]]
 name = "x-core"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "determinator",
  "diem-workspace-hack",
@@ -10374,7 +10374,7 @@ dependencies = [
 [[package]]
 name = "x-lint"
 version = "0.1.0"
-source = "git+https://github.com/starcoinorg/diem?rev=206386633cc7ef87a9efc7f35a33419a2174bfba#206386633cc7ef87a9efc7f35a33419a2174bfba"
+source = "git+https://github.com/starcoinorg/diem?rev=b96d25b270a9b3fc1301ac56951fccb7da40dc53#b96d25b270a9b3fc1301ac56951fccb7da40dc53"
 dependencies = [
  "diem-workspace-hack",
  "guppy",
```

### cmd/starcoin/Cargo.toml
```diff
@@ -44,7 +44,7 @@ starcoin-genesis = { path = "../../core/genesis" }
 starcoin-resource-viewer = { path = "../../vm/resource-viewer" }
 starcoin-service-registry = { path = "../../commons/service-registry" }
 starcoin-move-explain = { path = "../../vm/move-explain" }
-errmapgen = { git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
+errmapgen = { git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
 network-api = {path = "../../network/api", package="network-api"}
 
 [dev-dependencies]
```

### commons/crypto/Cargo.toml
```diff
@@ -11,8 +11,8 @@ serde = { version = "1.0.123" }
 serde_bytes = "0.11.5"
 hex = "0.4.2"
 anyhow = "1.0"
-diem-crypto = { package="diem-crypto",  git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba", features = ["fuzzing"] }
-diem-crypto-derive = { package="diem-crypto-derive",  git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
+diem-crypto = { package="diem-crypto",  git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53", features = ["fuzzing"] }
+diem-crypto-derive = { package="diem-crypto-derive",  git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
 bcs-ext = { package="bcs-ext", path = "../bcs_ext" }
 crypto-macro = { package="starcoin-crypto-macro", path = "./crypto-macro"}
 rand = "0.7.3"
```

### commons/proptest-helpers/Cargo.toml
```diff
@@ -8,7 +8,7 @@ edition = "2018"
 
 [dependencies]
 crossbeam = "0.7.3"
-diem-proptest-helpers = { package="diem-proptest-helpers",  git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
+diem-proptest-helpers = { package="diem-proptest-helpers",  git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
 
 proptest = "0.10.1"
 proptest-derive = "0.2.0"
```

### config/Cargo.toml
```diff
@@ -28,6 +28,6 @@ starcoin-types = { path = "../types" }
 starcoin-vm-types = { path = "../vm/types" }
 network-p2p-types = { path = "../network-p2p/types"}
 starcoin-logger = {path = "../commons/logger", package="starcoin-logger"}
-diem-temppath = { git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
+diem-temppath = { git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
 starcoin-system = {path = "../commons/system", package="starcoin-system"}
 network-api = {path = "../network/api", package="network-api"}
\ No newline at end of file
```

### devtools/x/Cargo.toml
```diff
@@ -23,7 +23,7 @@ globset = "0.4.6"
 regex = "1.4.3"
 rayon = "1.5.0"
 indexmap = "1.6.1"
-x-core = { package="x-core", git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
-x-lint = { package="x-lint", git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
-diem-workspace-hack = { package="diem-workspace-hack", git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
-diem-x = { package="x", git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
+x-core = { package="x-core", git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
+x-lint = { package="x-lint", git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
+diem-workspace-hack = { package="diem-workspace-hack", git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
+diem-x = { package="x", git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
```

### vm/compiler/Cargo.toml
```diff
@@ -11,8 +11,8 @@ anyhow = "1.0.38"
 once_cell = "1.5.2"
 tempfile = "3.1.0"
 regex = { version = "1.4.3", default-features = false, features = ["std", "perf"] }
-move-lang = { package="move-lang", git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
-move-lang-test-utils = { package="move-lang-test-utils", git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
+move-lang = { package="move-lang", git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
+move-lang-test-utils = { package="move-lang-test-utils", git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
 starcoin-crypto = { path = "../../commons/crypto"}
 starcoin-vm-types = { path = "../types"}
 starcoin-logger = { path = "../../commons/logger"}
```

### vm/functional-tests/Cargo.toml
```diff
@@ -9,7 +9,7 @@ edition = "2018"
 [dependencies]
 anyhow = "1.0.38"
 tempfile = "3.1.0"
-datatest-stable = {git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
+datatest-stable = {git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
 stdlib = { package="stdlib", path = "../stdlib"}
 once_cell = "1.5.2"
 regex = { version = "1.4.3", default-features = false, features = ["std", "perf"] }
@@ -30,7 +30,7 @@ executor = { package="starcoin-executor", path = "../../executor"}
 starcoin-genesis = { path = "../../core/genesis" }
 starcoin-consensus = { path = "../../consensus" }
 starcoin-account-api = { path = "../../account/api" }
-move-lang = { git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
+move-lang = { git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
 
 [dev-dependencies]
 starcoin-vm-types = { path = "../types"}
```

### vm/functional-tests/tests/testsuite/natives/bcs.move
```diff
@@ -0,0 +1,53 @@
+//! account: alice
+
+// Test for BCS to_address failure
+//! sender: alice
+script {
+    use 0x1::BCS;
+    fun main() {
+        let data = b"ff";
+        let _addr = BCS::to_address(data);
+    }
+}
+// check: "Keep(ABORTED { code: 454"
+
+
+//! new-transaction
+//! sender: alice
+// Test for BCS serialization in Move
+
+script {
+    use 0x1::BCS;
+
+    fun main() {
+        // address
+    let addr = 0x89b9f9d1fadc027cf9532d6f99041522;
+        let expected_output = x"89b9f9d1fadc027cf9532d6f99041522";
+        assert(BCS::to_bytes(&addr) == expected_output, 8001);
+
+        // bool
+    let b = true;
+        let expected_output = x"01";
+        assert(BCS::to_bytes(&b) == expected_output, 8002);
+
+        // u8
+    let i = 1u8;
+        let expected_output = x"01";
+        assert(BCS::to_bytes(&i) == expected_output, 8003);
+
+        // u64
+    let i = 1;
+        let expected_output = x"0100000000000000";
+        assert(BCS::to_bytes(&i) == expected_output, 8004);
+
+        // u128
+    let i = 1u128;
+        let expected_output = x"01000000000000000000000000000000";
+        assert(BCS::to_bytes(&i) == expected_output, 8005);
+
+        // vector<u8>
+    let v = x"0f";
+        let expected_output = x"010f";
+        assert(BCS::to_bytes(&v) == expected_output, 8006);
+    }
+}
```

### vm/functional-tests/tests/testsuite/natives/lcs.move
```diff
@@ -1,37 +0,0 @@
-// Test for BCS serialization in Move
-
-script {
-use 0x1::BCS;
-
-fun main() {
-    // address
-    let addr = 0x89b9f9d1fadc027cf9532d6f99041522;
-    let expected_output = x"89b9f9d1fadc027cf9532d6f99041522";
-    assert(BCS::to_bytes(&addr) == expected_output, 8001);
-
-    // bool
-    let b = true;
-    let expected_output = x"01";
-    assert(BCS::to_bytes(&b) == expected_output, 8002);
-
-    // u8
-    let i = 1u8;
-    let expected_output = x"01";
-    assert(BCS::to_bytes(&i) == expected_output, 8003);
-
-    // u64
-    let i = 1;
-    let expected_output = x"0100000000000000";
-    assert(BCS::to_bytes(&i) == expected_output, 8004);
-
-    // u128
-    let i = 1u128;
-    let expected_output = x"01000000000000000000000000000000";
-    assert(BCS::to_bytes(&i) == expected_output, 8005);
-
-    // vector<u8>
-    let v = x"0f";
-    let expected_output = x"010f";
-    assert(BCS::to_bytes(&v) == expected_output, 8006);
-}
-}
```

### vm/move-coverage/Cargo.toml
```diff
@@ -18,8 +18,8 @@ colored = "2.0.0"
 bcs-ext = { package="bcs-ext", path = "../../commons/bcs_ext" }
 starcoin-types = { path = "../../types"}
 starcoin-vm-types = { path = "../types"}
-bytecode-source-map = { package = "bytecode-source-map", version = "0.1.0", git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
-bytecode-verifier = { package = "bytecode-verifier", version = "0.1.0", git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
+bytecode-source-map = { package = "bytecode-source-map", version = "0.1.0", git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
+bytecode-verifier = { package = "bytecode-verifier", version = "0.1.0", git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
 
 [features]
 default = []
```

### vm/move-explain/Cargo.toml
```diff
@@ -12,9 +12,9 @@ edition = "2018"
 [dependencies]
 structopt = "0.3.21"
 stdlib = { package="stdlib", path = "../stdlib"}
-diem-workspace-hack = { git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
-errmapgen = { git = "https://github.com/starcoinorg/diem", rev="206386633cc7ef87a9efc7f35a33419a2174bfba" }
-move-core-types = { git = "https://github.com/starcoinorg/diem", rev = "206386633cc7ef87a9efc7f35a33419a2174bfba" }
+diem-workspace-hack = { git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
+errmapgen = { git = "https://github.com/starcoinorg/diem", rev="b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
+move-core-types = { git = "https://github.com/starcoinorg/diem", rev = "b96d25b270a9b3fc1301ac56951fccb7da40dc53" }
 bcs-ext = { package="bcs-ext", path = "../../commons/bcs_ext" }
 
 [features]
```
