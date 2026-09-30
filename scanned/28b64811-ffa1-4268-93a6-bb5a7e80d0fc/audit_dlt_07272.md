# [?] RUSTSEC-2021-0076 bump libsecp256k1 (#9391)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2021-08-16
Source: https://github.com/paritytech/substrate/commit/08cac0089d7539b29098b6ce773faf79a7944690
Type: security-commit

## Details
RUSTSEC-2021-0076 bump libsecp256k1 (#9391)

* RUSTSEC-2021-0076 bump libsecp256k1

libsecp256k1 allows overflowing signatures
https://rustsec.org/advisories/RUSTSEC-2021-0076

Changes were made to conform to libsecp256k1 version differences.

Closes #9356

* parse_standard_slice() -> parse_overflowing_slice()

* Added v2 host function for ecdsa_verify

* Add feature tag over helpers

* Added ecdsa_verify v2 to test runner

* PR feedback

- Spaces -> tabs
- renamed two helper functions

* Fixed imports after rebasing

* Bump rest of libsecp256k1 (and libp2p)

libp2p also uses libsecp256k1 so it is required to be bumped too, along
with all the version difference changes.

* Add version2 for ecdsa pubkey recovery

* libp2p rebase master fixes

* Fix test panic when non Behaviour event is returned

* Update bin/node/browser-testing/Cargo.toml

* Update primitives/core/src/ecdsa.rs

* Update primitives/core/src/ecdsa.rs

* Update Cargo.lock

Co-authored-by: Bastian Köcher <bkchr@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -38,58 +38,39 @@ checksum = "f26201604c87b1e01bd3d98f8d5d9a8fcbb815e8cedb41ffccbeb4bf593a35fe"
 
 [[package]]
 name = "aead"
-version = "0.3.2"
+version = "0.4.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7fc95d1bdb8e6666b2b217308eeeb09f2d6728d104be3e31916cc74d15420331"
+checksum = "6e3e798aa0c8239776f54415bc06f3d74b1850f3f830b45c35cfc80556973f70"
 dependencies = [
  "generic-array 0.14.4",
 ]
 
 [[package]]
 name = "aes"
-version = "0.5.0"
+version = "0.7.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dd2bc6d3f370b5666245ff421e231cba4353df936e26986d2918e61a8fd6aef6"
+checksum = "495ee669413bfbe9e8cace80f4d3d78e6d8c8d99579f97fb93bde351b185f2d4"
 dependencies = [
- "aes-soft",
- "aesni",
- "block-cipher",
+ "cfg-if 1.0.0",
+ "cipher",
+ "cpufeatures",
+ "opaque-debug 0.3.0",
 ]
 
 [[package]]
 name = "aes-gcm"
-version = "0.7.0"
+version = "0.9.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0301c9e9c443494d970a07885e8cf3e587bae8356a1d5abd0999068413f7205f"
+checksum = "b2a930fd487faaa92a30afa92cc9dd1526a5cff67124abbbb1c617ce070f4dcf"
 dependencies = [
  "aead",
  "aes",
- "block-cipher",
+ "cipher",
+ "ctr",
  "ghash",
  "subtle 2.4.0",
 ]
 
-[[package]]
-name = "aes-soft"
-version = "0.5.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "63dd91889c49327ad7ef3b500fd1109dbd3c509a03db0d4a9ce413b79f575cb6"
-dependencies = [
- "block-cipher",
- "byteorder",
- "opaque-debug 0.3.0",
-]
-
-[[package]]
-name = "aesni"
-version = "0.8.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0a6fe808308bb07d393e2ea47780043ec47683fcf19cf5efc8ca51c50cc8c68a"
-dependencies = [
- "block-cipher",
- "opaque-debug 0.3.0",
-]
-
 [[package]]
 name = "ahash"
 version = "0.4.7"
@@ -656,15 +637,6 @@ dependencies = [
  "generic-array 0.14.4",
 ]
 
-[[package]]
-name = "block-cipher"
-version = "0.8.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f337a3e6da609650eb74e02bc9fac7b735049f7623ab12f2e4c719316fcc7e80"
-dependencies = [
- "generic-array 0.14.4",
-]
-
 [[package]]
 name = "block-padding"
 version = "0.1.5"
@@ -811,7 +783,7 @@ version = "0.2.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4b9434b9a5aa1450faa3f9cb14ea0e8c53bb5d2b3c1bfd1ab4fc03e9f33fbfb0"
 dependencies = [
- "rustc_version",
+ "rustc_version 0.2.3",
 ]
 
 [[package]]
@@ -846,24 +818,26 @@ checksum = "baf1de4339761588bc0619e3cbc0120ee582ebb74b53b4efbf79117bd2da40fd"
 
 [[package]]
 name = "chacha20"
-version = "0.5.0"
+version = "0.7.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "244fbce0d47e97e8ef2f63b81d5e05882cb518c68531eb33194990d7b7e85845"
+checksum = "fee7ad89dc1128635074c268ee661f90c3f7e83d9fd12910608c36b47d6c3412"
 dependencies = [
- "stream-cipher",
+ "cfg-if 1.0.0",
+ "cipher",
+ "cpufeatures",
  "zeroize",
 ]
 
 [[package]]
 name = "chacha20poly1305"
-version = "0.6.0"
+version = "0.8.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9bf18d374d66df0c05cdddd528a7db98f78c28e2519b120855c4f84c5027b1f5"
+checksum = "1580317203210c517b6d44794abfbe600698276db18127e37ad3e69bf5e848e5"
 dependencies = [
  "aead",
  "chacha20",
+ "cipher",
  "poly1305",
- "stream-cipher",
  "zeroize",
 ]
 
@@ -903,15 +877,15 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ff0e3bc0b6446b3f9663c1a6aba6ef06c5aeaa1bc92bd18077be337198ab9768"
 dependencies = [
  "multibase",
- "multihash",
+ "multihash 0.13.2",
  "unsigned-varint 0.5.1",
 ]
 
 [[package]]
 name = "cipher"
-version = "0.2.5"
+version = "0.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "12f8e7987cbd042a63249497f41aed09f8e65add917ea6566effbc56578d6801"
+checksum = "7ee52072ec15386f770805afd189a01c8841be8696bed250fa2f13c4c0d6dfb7"
 dependencies = [
  "generic-array 0.14.4",
 ]
@@ -1012,16 +986,19 @@ dependencies = [
 ]
 
 [[package]]
-name = "cpuid-bool"
-version = "0.1.2"
+name = "cpufeatures"
+version = "0.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8aebca1129a03dc6dc2b127edd729435bbc4a37e1d5f4d7513165089ceb02634"
+checksum = "66c99696f6c9dd7f35d486b9d04d7e6e202aa3e8c40d553f2fdf5e7e0c6a71ef"
+dependencies = [
+ "libc",
+]
 
 [[package]]
 name = "cpuid-bool"
-version = "0.2.0"
+version = "0.1.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dcb25d077389e53838a8158c8e99174c5a9d902dee4904320db714f3c653ffba"
+checksum = "8aebca1129a03dc6dc2b127edd729435bbc4a37e1d5f4d7513165089ceb02634"
 
 [[package]]
 name = "cranelift-bforest"
@@ -1322,6 +1299,15 @@ dependencies = [
  "syn",
 ]
 
+[[package]]
+name = "ctr"
+version = "0.8.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "049bb91fb4aaf0e3c7efa6cd5ef877dbbbd15b39dad06d9948de4ec8a75761ea"
+dependencies = [
+ "cipher",
+]
+
 [[package]]
 name = "cuckoofilter"
 version = "0.5.0"
@@ -2272,9 +2258,9 @@ dependencies = [
 
 [[package]]
 name = "ghash"
-version = "0.3.1"
+version = "0.4.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "97304e4cd182c3846f7575ced3890c53012ce534ad9114046b0a9e00bb30a375"
+checksum = "b442c439366184de619215247d24e908912b175e824a530253845ac4c251a5c1"
 dependencies = [
  "opaque-debug 0.3.0",
  "polyval",
@@ -2440,13 +2426,13 @@ dependencies = [
 
 [[package]]
 name = "hmac-drbg"
-version = "0.2.0"
+version = "0.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c6e570451493f10f6581b48cdd530413b63ea9e780f544bfd3bdcaa0d89d1a7b"
+checksum = "17ea0a1394df5b6574da6e0c1ade9e78868c9fb0a4e5ef4428e32da4676b85b1"
 dependencies = [
- "digest 0.8.1",
- "generic-array 0.12.4",
- "hmac 0.7.1",
+ "digest 0.9.0",
+ "generic-array 0.14.4",
+ "hmac 0.8.1",
 ]
 
 [[package]]
@@ -3122,9 +3108,9 @@ checksum = "c7d73b3f436185384286bd8098d17ec07c9a7d2388a6599f824d8502b529702a"
 
 [[package]]
 name = "libp2p"
-version = "0.37.1"
+version = "0.39.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "08053fbef67cd777049ef7a95ebaca2ece370b4ed7712c3fa404d69a88cb741b"
+checksum = "9004c06878ef8f3b4b4067e69a140d87ed20bf777287f82223e49713b36ee433"
 dependencies = [
  "atomic",
  "bytes 1.0.1",
@@ -3152,7 +3138,7 @@ dependencies = [
  "libp2p-wasm-ext",
  "libp2p-websocket",
  "libp2p-yamux",
- "parity-multiaddr",
+ "multiaddr",
  "parking_lot 0.11.1",
  "pin-project 1.0.5",
  "smallvec 1.6.1",
@@ -3161,9 +3147,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-core"
-version = "0.28.2"
+version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "71dd51b562e14846e65bad00e5808d0644376e6588668c490d3c48e1dfeb4a9a"
+checksum = "af9b4abdeaa420593a297c8592f63fad4234f4b88dc9343b8fd8e736c35faa59"
 dependencies = [
  "asn1_der",
  "bs58",
@@ -3173,15 +3159,15 @@ dependencies = [
  "futures 0.3.16",
  "futures-timer 3.0.2",
  "lazy_static",
- "libsecp256k1",
+ "libsecp256k1 0.5.0",
  "log 0.4.14",
- "multihash",
+ "multiaddr",
+ "multihash 0.14.0",
  "multistream-select",
- "parity-multiaddr",
  "parking_lot 0.11.1",
  "pin-project 1.0.5",
- "prost",
- "prost-build",
+ "prost 0.8.0",
+ "prost-build 0.8.0",
  "rand 0.7.3",
  "ring",
  "rw-stream-sink",
@@ -3195,9 +3181,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-deflate"
-version = "0.28.0"
+version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a2181a641cd15f9b6ba71b1335800f309012a0a97a29ffaabbbf40e9d3d58f08"
+checksum = "66097fccc0b7f8579f90a03ea76ba6196332ea049fd07fd969490a06819dcdc8"
 dependencies = [
  "flate2",
  "futures 0.3.16",
@@ -3206,9 +3192,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-dns"
-version = "0.28.1"
+version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "62e63dab8b5ff35e0c101a3e51e843ba782c07bbb1682f5fd827622e0d02b98b"
+checksum = "58ff08b3196b85a17f202d80589e93b1660a574af67275706657fdc762e42c32"
 dependencies = [
  "async-std-resolver",
  "futures 0.3.16",
@@ -3220,27 +3206,27 @@ dependencies = [
 
 [[package]]
 name = "libp2p-floodsub"
-version = "0.29.0"
+version = "0.30.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "48a9b570f6766301d9c4aa00fce3554cad1598e2f466debbc4dde909028417cf"
+checksum = "404eca8720967179dac7a5b4275eb91f904a53859c69ca8d018560ad6beb214f"
 dependencies = [
  "cuckoofilter",
  "fnv",
  "futures 0.3.16",
  "libp2p-core",
  "libp2p-swarm",
  "log 0.4.14",
- "prost",
- "prost-build",
+ "prost 0.8.0",
+ "prost-build 0.8.0",
  "rand 0.7.3",
  "smallvec 1.6.1",
 ]
 
 [[package]]
 name = "libp2p-gossipsub"
-version = "0.30.0"
+version = "0.32.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "73cb9a89a301afde1e588c73f7e9131e12a5388725f290a9047b878862db1b53"
+checksum = "b1cc48709bcbc3a3321f08a73560b4bbb4166a7d56f6fdb615bc775f4f91058e"
 dependencies = [
  "asynchronous-codec 0.6.0",
  "base64 0.13.0",
@@ -3252,8 +3238,8 @@ dependencies = [
  "libp2p-core",
  "libp2p-swarm",
  "log 0.4.14",
- "prost",
- "prost-build",
+ "prost 0.8.0",
+ "prost-build 0.8.0",
  "rand 0.7.3",
  "regex",
  "sha2 0.9.3",
@@ -3264,25 +3250,25 @@ dependencies = [
 
 [[package]]
 name = "libp2p-identify"
-version = "0.29.0"
+version = "0.30.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5f668f00efd9883e8b7bcc582eaf0164615792608f886f6577da18bcbeea0a46"
+checksum = "a7b61f6cf07664fb97016c318c4d4512b3dd4cc07238607f3f0163245f99008e"
 dependencies = [
  "futures 0.3.16",
  "libp2p-core",
  "libp2p-swarm",
  "log 0.4.14",
- "prost",
- "prost-build",
+ "prost 0.8.0",
+ "prost-build 0.8.0",
  "smallvec 1.6.1",
  "wasm-timer",
 ]
 
 [[package]]
 name = "libp2p-kad"
-version = "0.30.0"
+version = "0.31.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b07312ebe5ee4fd2404447a0609814574df55c65d4e20838b957bbd34907d820"
+checksum = "50ed78489c87924235665a0ab345b298ee34dff0f7ad62c0ba6608b2144fb75e"
 dependencies = [
  "arrayvec 0.5.2",
  "asynchronous-codec 0.6.0",
@@ -3293,8 +3279,8 @@ dependencies = [
  "libp2p-core",
  "libp2p-swarm",
  "log 0.4.14",
- "prost",
- "prost-build",
+ "prost 0.8.0",
+ "prost-build 0.8.0",
  "rand 0.7.3",
  "sha2 0.9.3",
  "smallvec 1.6.1",
@@ -3306,9 +3292,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-mdns"
-version = "0.30.0"
+version = "0.31.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c221897b3fd7f215de7ecfec215c5eba598e5b61c605b5f8b56fe8a4fb507724"
+checksum = "a29e6cbc2a24b8471b6567e580a0e8e7b70a6d0f0ea2be0844d1e842d7d4fa33"
 dependencies = [
  "async-io",
  "data-encoding",
@@ -3327,9 +3313,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-mplex"
-version = "0.28.0"
+version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "85e9b544335d1ed30af71daa96edbefadef6f19c7a55f078b9fc92c87163105d"
+checksum = "313d9ea526c68df4425f580024e67a9d3ffd49f2c33de5154b1f5019816f7a99"
 dependencies = [
  "asynchronous-codec 0.6.0",
  "bytes 1.0.1",
@@ -3345,19 +3331,19 @@ dependencies = [
 
 [[package]]
 name = "libp2p-noise"
-version = "0.30.0"
+version = "0.32.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "36db0f0db3b0433f5b9463f1c0cd9eadc0a3734a9170439ce501ff99733a88bd"
+checksum = "3f1db7212f342b6ba7c981cc40e31f76e9e56cb48e65fa4c142ecaca5839523e"
 dependencies = [
  "bytes 1.0.1",
  "curve25519-dalek 3.0.2",
  "futures 0.3.16",
  "lazy_static",
  "libp2p-core",
  "log 0.4.14",
- "prost",
- "prost-build",
- "rand 0.7.3",
+ "prost 0.8.0",
+ "prost-build 0.8.0",
+ "rand 0.8.4",
  "sha2 0.9.3",
  "snow",
  "static_assertions",
@@ -3367,9 +3353,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-ping"
-version = "0.29.0"
+version = "0.30.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bf4bfaffac63bf3c7ec11ed9d8879d455966ddea7e78ee14737f0b6dce0d1cd1"
+checksum = "2482cfd9eb0b7a0baaf3e7b329dc4f2785181a161b1a47b7192f8d758f54a439"
 dependencies = [
  "futures 0.3.16",
  "libp2p-core",
@@ -3382,26 +3368,26 @@ dependencies = [
 
 [[package]]
 name = "libp2p-plaintext"
-version = "0.28.0"
+version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0c8c37b4d2a075b4be8442760a5f8c037180f0c8dd5b5734b9978ab868b3aa11"
+checksum = "13b4783e5423870b9a5c199f65a7a3bc66d86ab56b2b9beebf3c338d889cf8e4"
 dependencies = [
  "asynchronous-codec 0.6.0",
  "bytes 1.0.1",
  "futures 0.3.16",
  "libp2p-core",
  "log 0.4.14",
- "prost",
- "prost-build",
+ "prost 0.8.0",
+ "prost-build 0.8.0",
  "unsigned-varint 0.7.0",
  "void",
 ]
 
 [[package]]
 name = "libp2p-pnet"
-version = "0.20.0"
+version = "0.21.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6ce3374f3b28162db9d3442c9347c4f14cb01e8290052615c7d341d40eae0599"
+checksum = "07cb4dd4b917e5b40ddefe49b96b07adcd8d342e0317011d175b7b2bb1dcc974"
 dependencies = [
  "futures 0.3.16",
  "log 0.4.14",
@@ -3413,9 +3399,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-relay"
-version = "0.2.0"
+version = "0.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0b8786aca3f18671d8776289706a5521f6c9124a820f69e358de214b9939440d"
+checksum = "0133f6cfd81cdc16e716de2982e012c62e6b9d4f12e41967b3ee361051c622aa"
 dependencies = [
  "asynchronous-codec 0.6.0",
  "bytes 1.0.1",
@@ -3425,8 +3411,8 @@ dependencies = [
  "libp2p-swarm",
  "log 0.4.14",
  "pin-project 1.0.5",
- "prost",
- "prost-build",
+ "prost 0.8.0",
+ "prost-build 0.8.0",
  "rand 0.7.3",
  "smallvec 1.6.1",
  "unsigned-varint 0.7.0",
@@ -3436,9 +3422,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-request-response"
-version = "0.11.0"
+version = "0.12.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1cdbe172f08e6d0f95fa8634e273d4c4268c4063de2e33e7435194b0130c62e3"
+checksum = "06cdae44b6821466123af93cbcdec7c9e6ba9534a8af9cdc296446d39416d241"
 dependencies = [
  "async-trait",
  "bytes 1.0.1",
@@ -3456,9 +3442,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-swarm"
-version = "0.29.0"
+version = "0.30.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1e04d8e1eef675029ec728ba14e8d0da7975d84b6679b699b4ae91a1de9c3a92"
+checksum = "7083861341e1555467863b4cd802bea1e8c4787c0f7b5110097d0f1f3248f9a9"
 dependencies = [
  "either",
  "futures 0.3.16",
@@ -3472,19 +3458,19 @@ dependencies = [
 
 [[package]]
 name = "libp2p-swarm-derive"
-version = "0.23.0"
+version = "0.24.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "365b0a699fea5168676840567582a012ea297b1ca02eee467e58301b9c9c5eed"
+checksum = "ab8cb308d4fc854869f5abb54fdab0833d2cf670d407c745849dc47e6e08d79c"
 dependencies = [
  "quote",
  "syn",
 ]
 
 [[package]]
 name = "libp2p-tcp"
-version = "0.28.0"
+version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2b1a27d21c477951799e99d5c105d78868258502ce092988040a808d5a19bbd9"
+checksum = "79edd26b6b4bb5feee210dcda562dca186940dfecb0024b979c3f50824b3bf28"
 dependencies = [
  "async-io",
  "futures 0.3.16",
@@ -3499,9 +3485,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-uds"
-version = "0.28.0"
+version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ffd6564bb3b7ff203661ccbb69003c2b551e34cef974f2d6c6a28306a12170b5"
+checksum = "280e793440dd4e9f273d714f4497325c72cddb0fe85a49f9a03c88f41dd20182"
 dependencies = [
  "async-std",
  "futures 0.3.16",
@@ -3511,9 +3497,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-wasm-ext"
-version = "0.28.1"
+version = "0.29.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cef45d61e43c313531b5e903e4e8415212ff6338e0c54c47da5b9b412b5760de"
+checksum = "f553b7140fad3d7a76f50497b0ea591e26737d9607428a75509fc191e4d1b1f6"
 dependencies = [
  "futures 0.3.16",
  "js-sys",
@@ -3525,9 +3511,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-websocket"
-version = "0.29.0"
+version = "0.30.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cace60995ef6f637e4752cccbb2590f6bc358e8741a0d066307636c69a4b3a74"
+checksum = "ddf99dcbf5063e9d59087f61b1e85c686ceab2f5abedb472d32288065c0e5e27"
 dependencies = [
  "either",
  "futures 0.3.16",
@@ -3543,9 +3529,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-yamux"
-version = "0.32.0"
+version = "0.33.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f35da42cfc6d5cb0dcf3ad6881bc68d146cdf38f98655e09e33fbba4d13eabc4"
+checksum = "214cc0dd9c37cbed27f0bb1eba0c41bbafdb93a8be5e9d6ae1e6b4b42cd044bf"
 dependencies = [
  "futures 0.3.16",
  "libp2p-core",
@@ -3568,20 +3554,71 @@ dependencies = [
 
 [[package]]
 name = "libsecp256k1"
-version = "0.3.5"
+version = "0.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1fc1e2c808481a63dc6da2074752fdd4336a3c8fcc68b83db6f1fd5224ae7962"
+checksum = "bd1137239ab33b41aa9637a88a28249e5e70c40a42ccc92db7f12cc356c1fcd7"
 dependencies = [
  "arrayref",
- "crunchy",
- "digest 0.8.1",
+ "base64 0.12.3",
+ "digest 0.9.0",
  "hmac-drbg",
+ "libsecp256k1-core",
+ "libsecp256k1-gen-ecmult",
+ "libsecp256k1-gen-genmult",
  "rand 0.7.3",
- "sha2 0.8.2",
- "subtle 2.4.0",
+ "serde",
+ "sha2 0.9.3",
+ "typenum",
+]
+
+[[package]]
+name = "libsecp256k1"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c9d220bc1feda2ac231cb78c3d26f27676b8cf82c96971f7aeef3d0cf2797c73"
+dependencies = [
+ "arrayref",
+ "base64 0.12.3",
+ "digest 0.9.0",
+ "hmac-drbg",
+ "libsecp256k1-core",
+ "libsecp256k1-gen-ecmult",
+ "libsecp256k1-gen-genmult",
+ "rand 0.7.3",
+ "serde",
+ "sha2 0.9.3",
  "typenum",
 ]
 
+[[package]]
+name = "libsecp256k1-core"
+version = "0.2.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d0f6ab710cec28cef759c5f18671a27dae2a5f952cdaaee1d8e2908cb2478a80"
+dependencies = [
+ "crunchy",
+ "digest 0.9.0",
+ "subtle 2.4.0",
+]
+
+[[package]]
+name = "libsecp256k1-gen-ecmult"
+version = "0.2.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ccab96b584d38fac86a83f07e659f0deafd0253dc096dab5a36d53efe653c5c3"
+dependencies = [
+ "libsecp256k1-core",
+]
+
+[[package]]
+name = "libsecp256k1-gen-genmult"
+version = "0.2.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "67abfe149395e3aa1c48a2beb32b068e2334402df8181f818d3aee2b304c4f5d"
+dependencies = [
+ "libsecp256k1-core",
+]
+
 [[package]]
 name = "libz-sys"
 version = "1.1.2"
@@ -3956,6 +3993,24 @@ version = "0.2.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0debeb9fcf88823ea64d64e4a815ab1643f33127d995978e099942ce38f25238"
 
+[[package]]
+name = "multiaddr"
+version = "0.13.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "48ee4ea82141951ac6379f964f71b20876d43712bea8faf6dd1a375e08a46499"
+dependencies = [
+ "arrayref",
+ "bs58",
+ "byteorder",
+ "data-encoding",
+ "multihash 0.14.0",
+ "percent-encoding 2.1.0",
+ "serde",
+ "static_assertions",
+ "unsigned-varint 0.7.0",
+ "url 2.2.1",
+]
+
 [[package]]
 name = "multibase"
 version = "0.8.0"
@@ -3984,13 +4039,26 @@ dependencies = [
  "unsigned-varint 0.5.1",
 ]
 
+[[package]]
+name = "multihash"
+version = "0.14.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "752a61cd890ff691b4411423d23816d5866dd5621e4d1c5687a53b94b5a979d8"
+dependencies = [
+ "digest 0.9.0",
+ "generic-array 0.14.4",
+ "multihash-derive",
+ "sha2 0.9.3",
+ "unsigned-varint 0.7.0",
+]
+
 [[package]]
 name = "multihash-derive"
-version = "0.7.1"
+version = "0.7.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "85ee3c48cb9d9b275ad967a0e96715badc13c6029adb92f34fa17b9ff28fd81f"
+checksum = "424f6e86263cd5294cbd7f1e95746b95aca0e0d66bff31e5a40d6baa87b4aa99"
 dependencies = [
- "proc-macro-crate 0.1.5",
+ "proc-macro-crate 1.0.0",
  "proc-macro-error 1.0.4",
  "proc-macro2",
  "quote",
@@ -5708,24 +5776,6 @@ dependencies = [
  "snap",
 ]
 
-[[package]]
-name = "parity-multiaddr"
-version = "0.11.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "58341485071825827b7f03cf7efd1cb21e6a709bea778fb50227fd45d2f361b4"
-dependencies = [
- "arrayref",
- "bs58",
- "byteorder",
- "data-encoding",
- "multihash",
- "percent-encoding 2.1.0",
- "serde",
- "static_assertions",
- "unsigned-varint 0.7.0",
- "url 2.2.1",
-]
-
 [[package]]
 name = "parity-scale-codec"
 version = "2.2.0"
@@ -5846,7 +5896,7 @@ checksum = "f842b1982eb6c2fe34036a4fbfb06dd185a3f5c8edfaacdf7d1ea10b07de6252"
 dependencies = [
  "lock_api 0.3.4",
  "parking_lot_core 0.6.2",
- "rustc_version",
+ "rustc_version 0.2.3",
 ]
 
 [[package]]
@@ -5880,7 +5930,7 @@ dependencies = [
  "cloudabi",
  "libc",
  "redox_syscall 0.1.57",
- "rustc_version",
+ "rustc_version 0.2.3",
  "smallvec 0.6.14",
  "winapi 0.3.9",
 ]
@@ -6141,21 +6191,23 @@ dependencies = [
 
 [[package]]
 name = "poly1305"
-version = "0.6.2"
+version = "0.7.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4b7456bc1ad2d4cf82b3a016be4c2ac48daf11bf990c1603ebd447fe6f30fca8"
+checksum = "9fcffab1f78ebbdf4b93b68c1ffebc24037eedf271edaca795732b24e5e4e349"
 dependencies = [
- "cpuid-bool 0.2.0",
+ "cpufeatures",
+ "opaque-debug 0.3.0",
  "universal-hash",
 ]
 
 [[package]]
 name = "polyval"
-version = "0.4.5"
+version = "0.5.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "eebcc4aa140b9abd2bc40d9c3f7ccec842679cd79045ac3a7ac698c1a064b7cd"
+checksum = "a6ba6a405ef63530d6cb12802014b22f9c5751bd17cdcddbe9e46d5c8ae83287"
 dependencies = [
- "cpuid-bool 0.2.0",
+ "cfg-if 1.0.0",
+ "cpufeatures",
  "opaque-debug 0.3.0",
  "universal-hash",
 ]
@@ -6339,7 +6391,17 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9e6984d2f1a23009bd270b8bb56d0926810a3d483f59c987d77969e9d8e840b2"
 dependencies = [
  "bytes 1.0.1",
- "prost-derive",
+ "prost-derive 0.7.0",
+]
+
+[[package]]
+name = "prost"
+version = "0.8.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "de5e2533f59d08fcf364fd374ebda0692a70bd6d7e66ef97f306f45c6c5d8020"
+dependencies = [
+ "bytes 1.0.1",
+ "prost-derive 0.8.0",
 ]
 
 [[package]]
@@ -6354,8 +6416,26 @@ dependencies = [
  "log 0.4.14",
  "multimap",
  "petgraph",
- "prost",
- "prost-types",
+ "prost 0.7.0",
+ "prost-types 0.7.0",
+ "tempfile",
+ "which",
+]
+
+[[package]]
+name = "prost-build"
+version = "0.8.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "355f634b43cdd80724ee7848f95770e7e70eefa6dcf14fea676216573b8fd603"
+dependencies = [
+ "bytes 1.0.1",
+ "heck",
+ "itertools 0.10.0",
+ "log 0.4.14",
+ "multimap",
+ "petgraph",
+ "prost 0.8.0",
+ "prost-types 0.8.0",
  "tempfile",
  "which",
 ]
@@ -6373,14 +6453,37 @@ dependencies = [
  "syn",
 ]
 
+[[package]]
+name = "prost-derive"
+version = "0.8.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "600d2f334aa05acb02a755e217ef1ab6dea4d51b58b7846588b747edec04efba"
+dependencies = [
+ "anyhow",
+ "itertools 0.10.0",
+ "proc-macro2",
+ "quote",
+ "syn",
+]
+
 [[package]]
 name = "prost-types"
 version = "0.7.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b518d7cdd93dab1d1122cf07fa9a60771836c668dde9d9e2a139f957f0d9f1bb"
 dependencies = [
  "bytes 1.0.1",
- "prost",
+ "prost 0.7.0",
+]
+
+[[package]]
+name = "prost-types"
+version = "0.8.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "603bbd6394701d13f3f25aada59c7de9d35a6a5887cfc156181234a44002771b"
+dependencies = [
+ "bytes 1.0.1",
+ "prost 0.8.0",
 ]
 
 [[package]]
@@ -6962,6 +7065,15 @@ dependencies = [
  "semver 0.9.0",
 ]
 
+[[package]]
+name = "rustc_version"
+version = "0.3.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f0dfe2087c51c460008730de8b57e6a320782fbfb312e1f4d520e6c6fae155ee"
+dependencies = [
+ "semver 0.11.0",
+]
+
 [[package]]
 name = "rustls"
 version = "0.19.1"
@@ -7026,7 +7138,7 @@ version = "1.0.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6d3d055a2582e6b00ed7a31c1524040aa391092bf636328350813f3a0605215c"
 dependencies = [
- "rustc_version",
+ "rustc_version 0.2.3",
 ]
 
 [[package]]
@@ -7037,9 +7149,9 @@ checksum = "ef703b7cb59335eae2eb93ceb664c0eb7ea6bf567079d843e09420219668e072"
 
 [[package]]
 name = "salsa20"
-version = "0.7.2"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "399f290ffc409596022fce5ea5d4138184be4784f2b28c62c59f0d8389059a15"
+checksum = "ecbd2eb639fd7cab5804a0837fe373cc2172d15437e804c054a9fb885cb923b0"
 dependencies = [
  "cipher",
 ]
@@ -7075,8 +7187,8 @@ dependencies = [
  "libp2p",
  "log 0.4.14",
  "parity-scale-codec",
- "prost",
- "prost-build",
+ "prost 0.7.0",
+ "prost-build 0.7.0",
  "quickcheck",
  "rand 0.7.3",
  "sc-client-api",
@@ -7511,7 +7623,7 @@ version = "0.10.0-dev"
 dependencies = [
  "hex-literal",
  "lazy_static",
- "libsecp256k1",
+ "libsecp256k1 0.6.0",
  "log 0.4.14",
  "parity-scale-codec",
  "parking_lot 0.11.1",
@@ -7740,8 +7852,8 @@ dependencies = [
  "parity-scale-codec",
  "parking_lot 0.11.1",
  "pin-project 1.0.5",
- "prost",
- "prost-build",
+ "prost 0.7.0",
+ "prost-build 0.7.0",
  "quickcheck",
  "rand 0.7.3",
  "sc-block-builder",
@@ -8398,7 +8510,7 @@ checksum = "dfebf75d25bd900fd1e7d11501efab59bc846dbc76196839663e6637bba9f25f"
 dependencies = [
  "block-buffer 0.9.0",
  "cfg-if 1.0.0",
- "cpuid-bool 0.1.2",
+ "cpuid-bool",
  "digest 0.9.0",
  "opaque-debug 0.3.0",
 ]
@@ -8429,7 +8541,7 @@ checksum = "fa827a14b29ab7f44778d14a88d3cb76e949c45083f7dbfa507d0cb699dc12de"
 dependencies = [
  "block-buffer 0.9.0",
  "cfg-if 1.0.0",
- "cpuid-bool 0.1.2",
+ "cpuid-bool",
  "digest 0.9.0",
  "opaque-debug 0.3.0",
 ]
@@ -8536,17 +8648,17 @@ checksum = "45456094d1983e2ee2a18fdfebce3189fa451699d0502cb8e3b49dba5ba41451"
 
 [[package]]
 name = "snow"
-version = "0.7.2"
+version = "0.8.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "795dd7aeeee24468e5a32661f6d27f7b5cbed802031b2d7640c7b10f8fb2dd50"
+checksum = "6142f7c25e94f6fd25a32c3348ec230df9109b463f59c8c7acc4bd34936babb7"
 dependencies = [
  "aes-gcm",
  "blake2",
  "chacha20poly1305",
- "rand 0.7.3",
- "rand_core 0.5.1",
+ "rand 0.8.4",
+ "rand_core 0.6.2",
  "ring",
- "rustc_version",
+ "rustc_version 0.3.3",
  "sha2 0.9.3",
  "subtle 2.4.0",
  "x25519-dalek",
@@ -8856,7 +8968,7 @@ dependencies = [
  "hex-literal",
  "impl-serde",
  "lazy_static",
- "libsecp256k1",
+ "libsecp256k1 0.6.0",
  "log 0.4.14",
  "merlin",
  "num-traits",
@@ -8949,7 +9061,7 @@ version = "4.0.0-dev"
 dependencies = [
  "futures 0.3.16",
  "hash-db",
- "libsecp256k1",
+ "libsecp256k1 0.6.0",
  "log 0.4.14",
  "parity-scale-codec",
  "parking_lot 0.11.1",
@@ -9424,16 +9536,6 @@ dependencies = [
  "rand 0.8.4",
 ]
 
-[[package]]
-name = "stream-cipher"
-version = "0.7.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c80e15f898d8d8f25db24c253ea615cc14acf418ff307822995814e7d42cfa89"
-dependencies = [
- "block-cipher",
- "generic-array 0.14.4",
-]
-
 [[package]]
 name = "strsim"
 version = "0.8.0"
```

### Cargo.toml
```diff
@@ -221,8 +221,6 @@ members = [
 #
 # This list is ordered alphabetically.
 [profile.dev.package]
-aes-soft = { opt-level = 3 }
-aesni = { opt-level = 3 }
 blake2 = { opt-level = 3 }
 blake2-rfc = { opt-level = 3 }
 blake2b_simd = { opt-level = 3 }
```

### bin/node/cli/Cargo.toml
```diff
@@ -95,10 +95,8 @@ try-runtime-cli = { version = "0.10.0-dev", optional = true, path = "../../../ut
 # WASM-specific dependencies
 wasm-bindgen = { version = "0.2.73", optional = true }
 wasm-bindgen-futures = { version = "0.4.18", optional = true }
-browser-utils = { package = "substrate-browser-utils", path = "../../../utils/browser", optional = true, version = "0.10.0-dev" }
-libp2p-wasm-ext = { version = "0.28", features = [
-	"websocket",
-], optional = true }
+browser-utils = { package = "substrate-browser-utils", path = "../../../utils/browser", optional = true, version = "0.10.0-dev"}
+libp2p-wasm-ext = { version = "0.29", features = ["websocket"], optional = true }
 
 [target.'cfg(target_arch="x86_64")'.dependencies]
 node-executor = { version = "3.0.0-dev", path = "../executor", features = [
```

### client/authority-discovery/Cargo.toml
```diff
@@ -23,7 +23,7 @@ derive_more = "0.99.2"
 futures = "0.3.9"
 futures-timer = "3.0.1"
 ip_network = "0.4.0"
-libp2p = { version = "0.37.1", default-features = false, features = ["kad"] }
+libp2p = { version = "0.39.1", default-features = false, features = ["kad"] }
 log = "0.4.8"
 prometheus-endpoint = { package = "substrate-prometheus-endpoint", path = "../../utils/prometheus", version = "0.9.0" }
 prost = "0.7"
```

### client/cli/Cargo.toml
```diff
@@ -18,7 +18,7 @@ regex = "1.4.2"
 tokio = { version = "0.2.21", features = [ "signal", "rt-core", "rt-threaded", "blocking" ] }
 futures = "0.3.9"
 fdlimit = "0.2.1"
-libp2p = "0.37.1"
+libp2p = "0.39.1"
 parity-scale-codec = "2.0.0"
 hex = "0.4.2"
 rand = "0.7.3"
```

### client/consensus/common/Cargo.toml
```diff
@@ -14,7 +14,7 @@ targets = ["x86_64-unknown-linux-gnu"]
 
 [dependencies]
 thiserror = "1.0.21"
-libp2p = { version = "0.37.1", default-features = false }
+libp2p = { version = "0.39.1", default-features = false }
 log = "0.4.8"
 futures = { version = "0.3.1", features = ["thread-pool"] }
 futures-timer = "3.0.1"
```

### client/executor/Cargo.toml
```diff
@@ -32,7 +32,7 @@ sc-executor-wasmi = { version = "0.10.0-dev", path = "wasmi" }
 sc-executor-wasmtime = { version = "0.10.0-dev", path = "wasmtime", optional = true }
 parking_lot = "0.11.1"
 log = "0.4.8"
-libsecp256k1 = "0.3.4"
+libsecp256k1 = "0.6"
 
 [dev-dependencies]
 wat = "1.0"
```

### client/network-gossip/Cargo.toml
```diff
@@ -17,7 +17,7 @@ targets = ["x86_64-unknown-linux-gnu"]
 [dependencies]
 futures = "0.3.9"
 futures-timer = "3.0.1"
-libp2p = { version = "0.37.1", default-features = false }
+libp2p = { version = "0.39.1", default-features = false }
 log = "0.4.8"
 lru = "0.6.5"
 prometheus-endpoint = { package = "substrate-prometheus-endpoint", version = "0.9.0", path = "../../utils/prometheus" }
```

### client/network/Cargo.toml
```diff
@@ -67,10 +67,10 @@ wasm-timer = "0.2"
 zeroize = "1.2.0"
 
 [dependencies.libp2p]
-version = "0.37.1"
+version = "0.39.1"
 
 [target.'cfg(target_os = "unknown")'.dependencies.libp2p]
-version = "0.37.1"
+version = "0.39.1"
 default-features = false
 features = [
     "identify",
@@ -88,7 +88,7 @@ features = [
 
 [dev-dependencies]
 assert_matches = "1.3"
-libp2p = { version = "0.37.1", default-features = false }
+libp2p = { version = "0.39.1", default-features = false }
 quickcheck = "1.0.3"
 rand = "0.7.2"
 sp-test-primitives = { version = "2.0.0", path = "../../primitives/test-primitives" }
```

### client/network/src/bitswap.rs
```diff
@@ -94,7 +94,7 @@ where
 
 	fn upgrade_inbound(self, mut socket: TSocket, _info: Self::Info) -> Self::Future {
 		Box::pin(async move {
-			let packet = upgrade::read_one(&mut socket, MAX_PACKET_SIZE).await?;
+			let packet = upgrade::read_length_prefixed(&mut socket, MAX_PACKET_SIZE).await?;
 			let message: BitswapMessage = Message::decode(packet.as_slice())?;
 			Ok(message)
 		})
@@ -122,7 +122,7 @@ where
 		Box::pin(async move {
 			let mut data = Vec::with_capacity(self.encoded_len());
 			self.encode(&mut data)?;
-			upgrade::write_one(&mut socket, data).await
+			upgrade::write_length_prefixed(&mut socket, data).await
 		})
 	}
 }
@@ -328,7 +328,7 @@ pub enum BitswapError {
 	/// Error parsing CID
 	BadCid(cid::Error),
 	/// Packet read error.
-	Read(upgrade::ReadOneError),
+	Read(io::Error),
 	/// Error sending response.
 	#[display(fmt = "Failed to send response.")]
 	SendResponse,
```

### client/network/src/discovery.rs
```diff
@@ -722,7 +722,7 @@ impl NetworkBehaviour for DiscoveryBehaviour {
 						KademliaEvent::PendingRoutablePeer { .. } => {
 							// We are not interested in this event at the moment.
 						},
-						KademliaEvent::QueryResult {
+						KademliaEvent::OutboundQueryCompleted {
 							result: QueryResult::GetClosestPeers(res),
 							..
 						} => match res {
@@ -741,7 +741,7 @@ impl NetworkBehaviour for DiscoveryBehaviour {
 								}
 							},
 						},
-						KademliaEvent::QueryResult {
+						KademliaEvent::OutboundQueryCompleted {
 							result: QueryResult::GetRecord(res),
 							stats,
 							..
@@ -778,7 +778,7 @@ impl NetworkBehaviour for DiscoveryBehaviour {
 							};
 							return Poll::Ready(NetworkBehaviourAction::GenerateEvent(ev))
 						},
-						KademliaEvent::QueryResult {
+						KademliaEvent::OutboundQueryCompleted {
 							result: QueryResult::PutRecord(res),
 							stats,
 							..
@@ -799,7 +799,7 @@ impl NetworkBehaviour for DiscoveryBehaviour {
 							};
 							return Poll::Ready(NetworkBehaviourAction::GenerateEvent(ev))
 						},
-						KademliaEvent::QueryResult {
+						KademliaEvent::OutboundQueryCompleted {
 							result: QueryResult::RepublishRecord(res),
 							..
 						} => match res {
@@ -830,6 +830,11 @@ impl NetworkBehaviour for DiscoveryBehaviour {
 							address,
 							score,
 						}),
+					NetworkBehaviourAction::CloseConnection { peer_id, connection } =>
+						return Poll::Ready(NetworkBehaviourAction::CloseConnection {
+							peer_id,
+							connection,
+						}),
 				}
 			}
 		}
@@ -862,6 +867,11 @@ impl NetworkBehaviour for DiscoveryBehaviour {
 						address,
 						score,
 					}),
+				NetworkBehaviourAction::CloseConnection { peer_id, connection } =>
+					return Poll::Ready(NetworkBehaviourAction::CloseConnection {
+						peer_id,
+						connection,
+					}),
 			}
 		}
 
@@ -931,7 +941,7 @@ mod tests {
 		},
 		identity::Keypair,
 		noise,
-		swarm::Swarm,
+		swarm::{Swarm, SwarmEvent},
 		yamux, Multiaddr, PeerId,
 	};
 	use std::{collections::HashSet, task::Poll};
@@ -1000,32 +1010,42 @@ mod tests {
 					match swarms[swarm_n].0.poll_next_unpin(cx) {
 						Poll::Ready(Some(e)) => {
 							match e {
-								DiscoveryOut::UnroutablePeer(other) |
-								DiscoveryOut::Discovered(other) => {
-									// Call `add_self_reported_address` to simulate identify
-									// happening.
-									let addr = swarms
-										.iter()
-										.find_map(|(s, a)| {
-											if s.behaviour().local_peer_id == other {
-												Some(a.clone())
-											} else {
-												None
-											}
-										})
-										.unwrap();
-									swarms[swarm_n].0.behaviour_mut().add_self_reported_address(
-										&other,
-										[protocol_name_from_protocol_id(&protocol_id)].iter(),
-										addr,
-									);
-
-									to_discover[swarm_n].remove(&other);
-								},
-								DiscoveryOut::RandomKademliaStarted(_) => {},
-								e => {
-									panic!("Unexpected event: {:?}", e)
+								SwarmEvent::Behaviour(behavior) => {
+									match behavior {
+										DiscoveryOut::UnroutablePeer(other) |
+										DiscoveryOut::Discovered(other) => {
+											// Call `add_self_reported_address` to simulate identify
+											// happening.
+											let addr = swarms
+												.iter()
+												.find_map(|(s, a)| {
+													if s.behaviour().local_peer_id == other {
+														Some(a.clone())
+													} else {
+														None
+													}
+												})
+												.unwrap();
+											swarms[swarm_n]
+												.0
+												.behaviour_mut()
+												.add_self_reported_address(
+													&other,
+													[protocol_name_from_protocol_id(&protocol_id)]
+														.iter(),
+													addr,
+												);
+
+											to_discover[swarm_n].remove(&other);
+										},
+										DiscoveryOut::RandomKademliaStarted(_) => {},
+										e => {
+											panic!("Unexpected event: {:?}", e)
+										},
+									}
 								},
+								// ignore non Behaviour events
+								_ => {},
 							}
 							continue 'polling
 						},
```

### client/network/src/peer_info.rs
```diff
@@ -340,6 +340,11 @@ impl NetworkBehaviour for PeerInfoBehaviour {
 						address,
 						score,
 					}),
+				Poll::Ready(NetworkBehaviourAction::CloseConnection { peer_id, connection }) =>
+					return Poll::Ready(NetworkBehaviourAction::CloseConnection {
+						peer_id,
+						connection,
+					}),
 			}
 		}
 
@@ -373,6 +378,11 @@ impl NetworkBehaviour for PeerInfoBehaviour {
 						address,
 						score,
 					}),
+				Poll::Ready(NetworkBehaviourAction::CloseConnection { peer_id, connection }) =>
+					return Poll::Ready(NetworkBehaviourAction::CloseConnection {
+						peer_id,
+						connection,
+					}),
 			}
 		}
 
```
