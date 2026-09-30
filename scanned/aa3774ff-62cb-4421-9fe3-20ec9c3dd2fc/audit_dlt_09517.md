# [?] chore: update dependency and config.toml for RUSTSEC-2023-0065 (#4066)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2023-10-02
Source: https://github.com/chainflip-io/chainflip-backend/commit/b3adda0311dabae842cbb12c8367120f65a97b64
Type: security-commit

## Details
chore: update dependency and config.toml for RUSTSEC-2023-0065 (#4066)

## Patch
### .cargo/config.toml
```diff
@@ -37,6 +37,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2021-0060: This is a transitive dependency of libp2p and will be fixed in an upcoming release.
 # - RUSTSEC-2021-0059: This is a transitive dependency of libp2p and will be fixed in an upcoming release.
 # - RUSTSEC-2023-0063: This is a transitive dependency of libp2p and it is not used.
+# - RUSTSEC-2023-0065: This is a transitive dependency of ethers and is only applicable when using as a server for untrusted traffic.
 cf-audit = '''
 audit --ignore RUSTSEC-2022-0061
       --ignore RUSTSEC-2020-0071
@@ -49,4 +50,5 @@ audit --ignore RUSTSEC-2022-0061
       --ignore RUSTSEC-2021-0060
       --ignore RUSTSEC-2021-0059
       --ignore RUSTSEC-2023-0063
+      --ignore RUSTSEC-2023-0065
 '''
```

### Cargo.lock
```diff
@@ -12193,29 +12193,29 @@ dependencies = [
 
 [[package]]
 name = "tokio-tungstenite"
-version = "0.18.0"
+version = "0.19.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "54319c93411147bced34cb5609a80e0a8e44c5999c93903a81cd866630ec0bfd"
+checksum = "ec509ac96e9a0c43427c74f003127d953a265737636129424288d27cb5c4b12c"
 dependencies = [
  "futures-util",
  "log",
+ "rustls 0.21.6",
  "tokio",
- "tungstenite 0.18.0",
+ "tokio-rustls 0.24.1",
+ "tungstenite 0.19.0",
+ "webpki-roots 0.23.1",
 ]
 
 [[package]]
 name = "tokio-tungstenite"
-version = "0.19.0"
+version = "0.20.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ec509ac96e9a0c43427c74f003127d953a265737636129424288d27cb5c4b12c"
+checksum = "212d5dcb2a1ce06d81107c3d0ffa3121fe974b73f068c8282cb1c32328113b6c"
 dependencies = [
  "futures-util",
  "log",
- "rustls 0.21.6",
  "tokio",
- "tokio-rustls 0.24.1",
- "tungstenite 0.19.0",
- "webpki-roots 0.23.1",
+ "tungstenite 0.20.1",
 ]
 
 [[package]]
@@ -12611,28 +12611,30 @@ checksum = "f4f195fd851901624eee5a58c4bb2b4f06399148fcd0ed336e6f1cb60a9881df"
 
 [[package]]
 name = "tungstenite"
-version = "0.18.0"
+version = "0.19.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "30ee6ab729cd4cf0fd55218530c4522ed30b7b6081752839b68fcec8d0960788"
+checksum = "15fba1a6d6bb030745759a9a2a588bfe8490fc8b4751a277db3a0be1c9ebbf67"
 dependencies = [
- "base64 0.13.1",
  "byteorder",
  "bytes",
+ "data-encoding",
  "http",
  "httparse",
  "log",
  "rand 0.8.5",
+ "rustls 0.21.6",
  "sha1",
  "thiserror",
  "url",
  "utf-8",
+ "webpki 0.22.0",
 ]
 
 [[package]]
 name = "tungstenite"
-version = "0.19.0"
+version = "0.20.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "15fba1a6d6bb030745759a9a2a588bfe8490fc8b4751a277db3a0be1c9ebbf67"
+checksum = "9e3dac10fd62eaf6617d3a904ae222845979aec67c615d1c842b4002c7666fb9"
 dependencies = [
  "byteorder",
  "bytes",
@@ -12641,12 +12643,10 @@ dependencies = [
  "httparse",
  "log",
  "rand 0.8.5",
- "rustls 0.21.6",
  "sha1",
  "thiserror",
  "url",
  "utf-8",
- "webpki 0.22.0",
 ]
 
 [[package]]
@@ -12917,9 +12917,9 @@ dependencies = [
 
 [[package]]
 name = "warp"
-version = "0.3.5"
+version = "0.3.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ba431ef570df1287f7f8b07e376491ad54f84d26ac473489427231e1718e1f69"
+checksum = "c1e92e22e03ff1230c03a1a8ee37d2f89cd489e2e541b7550d6afad96faed169"
 dependencies = [
  "bytes",
  "futures-channel",
@@ -12940,7 +12940,7 @@ dependencies = [
  "serde_urlencoded",
  "tokio",
  "tokio-stream",
- "tokio-tungstenite 0.18.0",
+ "tokio-tungstenite 0.20.1",
  "tokio-util",
  "tower-service",
  "tracing",
```

### engine/Cargo.toml
```diff
@@ -84,7 +84,7 @@ x25519-dalek = { version = "1.1", features = ["serde"] }
 zmq = { git = "https://github.com/chainflip-io/rust-zmq.git", tag = "chainflip-v0.9.2+1", features = [
   "vendored",
 ] }
-warp = { version = "0.3.5" }
+warp = { version = "0.3.6" }
 
 # Local deps
 cf-chains = { path = "../state-chain/chains" }
```
