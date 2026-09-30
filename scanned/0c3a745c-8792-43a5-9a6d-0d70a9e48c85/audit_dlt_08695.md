# [?] Merge branch 'master' into fix/blocks-reexecutor-shutdown-panic

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-20
Source: https://github.com/OffchainLabs/nitro/commit/139b87634122f1a86dfa8abb3a9f7926b9b78c3a
Type: security-commit

## Details
Merge branch 'master' into fix/blocks-reexecutor-shutdown-panic

## Patch
### Cargo.lock
```diff
@@ -185,7 +185,7 @@ checksum = "ce8849c74c9ca0f5a03da1c865e3eb6f768df816e67dd3721a398a8a7e398011"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -242,7 +242,7 @@ dependencies = [
  "darling 0.21.3",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -454,7 +454,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "62945a2f7e6de02a31fe400aa489f0e0f5b2502e69f95f853adb82a96c7a6b60"
 dependencies = [
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -492,7 +492,7 @@ dependencies = [
  "num-traits",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -560,9 +560,9 @@ dependencies = [
 
 [[package]]
 name = "arrayvec"
-version = "0.7.6"
+version = "0.7.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7c02d123df017efcdfbd739ef81735b36c5ba83ec3c59c80a9d7ecc718f92e50"
+checksum = "96d30a06541fbafbc7f82ed10c06164cfbd2c401138f6addd8404629c4b16711"
 
 [[package]]
 name = "atomic-waker"
@@ -589,7 +589,7 @@ checksum = "ffdcb70bdbc4d478427380519163274ac86e52916e10f0a8889adf0f96d3fee7"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -756,15 +756,15 @@ dependencies = [
  "bitflags 2.11.0",
  "cexpr",
  "clang-sys",
- "itertools 0.10.5",
+ "itertools 0.13.0",
  "log",
  "prettyplease",
  "proc-macro2",
  "quote",
  "regex",
  "rustc-hash",
  "shlex",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -834,9 +834,9 @@ dependencies = [
 
 [[package]]
 name = "block-buffer"
-version = "0.11.0"
+version = "0.12.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "96eb4cdd6cf1b31d671e9efe75c5d1ec614776856cefbe109ca373554a6d514f"
+checksum = "cdd35008169921d80bc60d3d0ab416eecb028c4cd653352907921d95084790be"
 dependencies = [
  "hybrid-array",
 ]
@@ -873,7 +873,7 @@ dependencies = [
  "proc-macro-crate",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -921,7 +921,7 @@ checksum = "89385e82b5d1821d2219e0b095efa2cc1f246cbf99080f3be46a1a85c0d392d9"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1122,7 +1122,7 @@ dependencies = [
  "heck 0.5.0",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1229,9 +1229,9 @@ checksum = "06ea2b9bc92be3c2baa9334a323ebca2d6f074ff852cd1d7b11064035cd3868f"
 
 [[package]]
 name = "corosensei"
-version = "0.3.2"
+version = "0.3.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2b2b4c7e3e97730e6b0b8c5ff5ca82c663d1a645e4f630f4fa4c24e80626787e"
+checksum = "2c54787b605c7df106ceccf798df23da4f2e09918defad66705d1cedf3bb914f"
 dependencies = [
  "autocfg",
  "cfg-if 1.0.0",
@@ -1506,9 +1506,9 @@ dependencies = [
 
 [[package]]
 name = "crypto-common"
-version = "0.2.0"
+version = "0.2.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "211f05e03c7d03754740fd9e585de910a095d6b99f8bcfffdef8319fa02a8331"
+checksum = "77727bb15fa921304124b128af125e7e3b968275d1b108b379190264f4423710"
 dependencies = [
  "hybrid-array",
 ]
@@ -1544,7 +1544,7 @@ dependencies = [
  "proc-macro2",
  "quote",
  "strsim 0.11.1",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1559,7 +1559,7 @@ dependencies = [
  "quote",
  "serde",
  "strsim 0.11.1",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1570,7 +1570,7 @@ checksum = "d336a2a514f6ccccaa3e09b02d41d35330c07ddf03a62165fcec10bb561c7806"
 dependencies = [
  "darling_core 0.20.10",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1581,7 +1581,7 @@ checksum = "d38308df82d1080de0afee5d069fa14b0326a88c14f15c5ccda35b4a6c414c81"
 dependencies = [
  "darling_core 0.21.3",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1639,7 +1639,7 @@ dependencies = [
  "proc-macro2",
  "quote",
  "rustc_version 0.4.0",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1661,7 +1661,7 @@ dependencies = [
  "proc-macro2",
  "quote",
  "rustc_version 0.4.0",
- "syn 2.0.114",
+ "syn 2.0.117",
  "unicode-xid",
 ]
 
@@ -1688,13 +1688,13 @@ dependencies = [
 
 [[package]]
 name = "digest"
-version = "0.11.0-rc.11"
+version = "0.11.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "02b42f1d9edf5207c137646b568a0168ca0ec25b7f9eaf7f9961da51a3d91cea"
+checksum = "4850db49bf08e663084f7fb5c87d202ef91a3907271aff24a94eb97ff039153c"
 dependencies = [
- "block-buffer 0.11.0",
+ "block-buffer 0.12.0",
  "const-oid 0.10.2",
- "crypto-common 0.2.0",
+ "crypto-common 0.2.1",
 ]
 
 [[package]]
@@ -1705,7 +1705,7 @@ checksum = "97369cbbc041bc366949bc74d34658d6cda5621039731c6310521892a3a20ae0"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1726,7 +1726,7 @@ dependencies = [
  "proc-macro-error2",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1738,7 +1738,7 @@ dependencies = [
  "byteorder",
  "dynasm",
  "fnv",
- "memmap2 0.9.9",
+ "memmap2 0.9.10",
 ]
 
 [[package]]
@@ -1765,7 +1765,7 @@ dependencies = [
  "enum-ordinalize",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1823,7 +1823,7 @@ checksum = "685adfa4d6f3d765a26bc5dbc936577de9abf756c1feeb3089b01dd395034842"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1843,7 +1843,7 @@ checksum = "8ca9601fb2d62598ee17836250842873a413586e5d7ed88b356e38ddbb0ec631"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -1864,15 +1864,9 @@ dependencies = [
  "darling 0.20.10",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
-[[package]]
-name = "env_home"
-version = "0.1.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c7f84e12ccf0a7ddc17a6c41c93326024c42920d7ee630d04950e6926645c0fe"
-
 [[package]]
 name = "equivalent"
 version = "1.0.1"
@@ -1886,7 +1880,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"
 dependencies = [
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -2373,9 +2367,9 @@ checksum = "df3b46402a9d5adb4c86a0cf463f42e19994e3ee891101b1841f30a545cb49a9"
 
 [[package]]
 name = "hybrid-array"
-version = "0.4.7"
+version = "0.4.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e1b229d73f5803b562cc26e4da0396c8610a4ee209f4fac8fa4f8d709166dc45"
+checksum = "8655f91cd07f2b9d0c24137bd650fe69617773435ee5ec83022377777ce65ef1"
 dependencies = [
  "typenum",
 ]
@@ -2652,7 +2646,7 @@ checksum = "63736175c9a30ea123f7018de9f26163e0b39cd6978990ae486b510c4f3bad69"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -2679,7 +2673,7 @@ checksum = "3640c1c38b8e4e43584d8df18be5fc6b0aa314ce6ebf51b53313d4306cca8e46"
 dependencies = [
  "hermit-abi 0.5.2",
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -2877,13 +2871,14 @@ checksum = "b6d2cec3eae94f9f509c767b45932f1ada8350c4bdb85af2fcab4a3c14807981"
 
 [[package]]
 name = "libredox"
-version = "0.1.12"
+version = "0.1.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3d0b95e02c851351f877147b7deea7b1afb1df71b63aa5f8270716e0c5720616"
+checksum = "1744e39d1d6a9948f4f388969627434e31128196de472883b39f148769bfe30a"
 dependencies = [
  "bitflags 2.11.0",
  "libc",
- "redox_syscall 0.7.0",
+ "plain",
+ "redox_syscall 0.7.3",
 ]
 
 [[package]]
@@ -3007,9 +3002,9 @@ dependencies = [
 
 [[package]]
 name = "memmap2"
-version = "0.9.9"
+version = "0.9.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "744133e4a0e0a658e1374cf3bf8e415c4052a15a111acd372764c55b4177d490"
+checksum = "714098028fe011992e1c3962653c96b2d578c4b4bce9036e15ff220319b1e0e3"
 dependencies = [
  "libc",
 ]
@@ -3094,7 +3089,7 @@ checksum = "4568f25ccbd45ab5d5603dc34318c1ec56b117531781260002151b8530a9f931"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -3163,7 +3158,7 @@ checksum = "ed3955f1a9c7c0c15e092f9c887db08b1fc683305fdf6eb6684f22555355e202"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -3235,7 +3230,7 @@ dependencies = [
  "proc-macro-crate",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -3405,7 +3400,7 @@ dependencies = [
  "phf_shared",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -3445,6 +3440,12 @@ version = "0.3.30"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d231b230927b5e4ad203db57bbcbee2802f6bce620b1e4a9024a07d94e2907ec"
 
+[[package]]
+name = "plain"
+version = "0.2.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "b4596b6d070b27117e987119b4dac604f3c58cfb0b191112e24771b2faeac1a6"
+
 [[package]]
 name = "plotters"
 version = "0.3.6"
@@ -3504,7 +3505,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "479ca8adacdd7ce8f1fb39ce9ecccbfe93a3f1344b3d0d97f20bc0196208f62b"
 dependencies = [
  "proc-macro2",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -3570,7 +3571,7 @@ dependencies = [
  "proc-macro-error-attr2",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -3667,7 +3668,7 @@ checksum = "7347867d0a7e1208d93b46767be83e2b8f978c3dad35f775ac8d8847551d6fe1"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -3729,14 +3730,14 @@ dependencies = [
  "once_cell",
  "socket2",
  "tracing",
- "windows-sys 0.52.0",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
 name = "quote"
-version = "1.0.44"
+version = "1.0.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "21b2ebcf727b7760c461f091f9f0f539b77b8e87f2fd88131e7f1b433b3cece4"
+checksum = "41f2619966050689382d2b44f664f4bc593e129785a36d6ee376ddf37259b924"
 dependencies = [
  "proc-macro2",
 ]
@@ -3894,9 +3895,9 @@ dependencies = [
 
 [[package]]
 name = "redox_syscall"
-version = "0.7.0"
+version = "0.7.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "49f3fe0889e69e2ae9e41f4d6c4c0181701d00e4697b356fb1f74173a5e0ee27"
+checksum = "6ce70a74e890531977d37e532c34d45e9055d2409ed08ddba14529471ed0be16"
 dependencies = [
  "bitflags 2.11.0",
 ]
@@ -3917,9 +3918,9 @@ dependencies = [
 
 [[package]]
 name = "regex"
-version = "1.12.2"
+version = "1.12.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "843bc0191f75f3e22651ae5f1e72939ab2f72a4bc30fa80a066bd66edefc24d4"
+checksum = "e10754a14b9137dd7b1e3e5b0493cc9171fdd105e0ab477f51b72e7f3ac0e276"
 dependencies = [
  "aho-corasick",
  "memchr",
@@ -3929,9 +3930,9 @@ dependencies = [
 
 [[package]]
 name = "regex-automata"
-version = "0.4.13"
+version = "0.4.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5276caf25ac86c8d810222b3dbb938e512c55c6831a10f3e6ed1c93b84041f1c"
+checksum = "6e1dd4122fc1595e8162618945476892eefca7b88c52820e74af6262213cae8f"
 dependencies = [
  "aho-corasick",
  "memchr",
@@ -3946,9 +3947,9 @@ checksum = "cab834c73d247e67f4fae452806d17d3c7501756d98c8808d7c9c7aa7d18f973"
 
 [[package]]
 name = "regex-syntax"
-version = "0.8.8"
+version = "0.8.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7a2d987857b319362043e95f5353c0535c1f58eec5336fdfcf626430af7def58"
+checksum = "dc897dd8d9e8bd1ed8cdad82b5966c3e0ecae09fb1907d58efaa013543185d0a"
 
 [[package]]
 name = "region"
@@ -4035,9 +4036,9 @@ dependencies = [
 
 [[package]]
 name = "rkyv"
-version = "0.8.14"
+version = "0.8.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "360b333c61ae24e5af3ae7c8660bd6b21ccd8200dbbc5d33c2454421e85b9c69"
+checksum = "1a30e631b7f4a03dee9056b8ef6982e8ba371dd5bedb74d3ec86df4499132c70"
 dependencies = [
  "bytecheck",
  "bytes",
@@ -4054,13 +4055,13 @@ dependencies = [
 
 [[package]]
 name = "rkyv_derive"
-version = "0.8.14"
+version = "0.8.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7c02f8cdd12b307ab69fe0acf4cd2249c7460eb89dce64a0febadf934ebb6a9e"
+checksum = "8100bb34c0a1d0f907143db3149e6b4eea3c33b9ee8b189720168e818303986f"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -4228,7 +4229,7 @@ dependencies = [
  "security-framework",
  "security-framework-sys",
  "webpki-root-certs",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -4433,7 +4434,7 @@ checksum = "d540f220d3187173da220f885ab66608367b6574e925011a9353e4badda91d79"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -4498,7 +4499,7 @@ dependencies = [
  "darling 0.20.10",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -4541,7 +4542,7 @@ checksum = "7c5f3b1e2dc8aad28310d8410bd4d7e180eca65fca176c52ab00d364475d0024"
 dependencies = [
  "cfg-if 1.0.0",
  "cpufeatures",
- "digest 0.11.0-rc.11",
+ "digest 0.11.2",
 ]
 
 [[package]]
@@ -4755,7 +4756,7 @@ dependencies = [
  "heck 0.5.0",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -4803,9 +4804,9 @@ dependencies = [
 
 [[package]]
 name = "syn"
-version = "2.0.114"
+version = "2.0.117"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d4d107df263a3013ef9b1879b0df87d706ff80f65a86ea879bd9c31f9b307c2a"
+checksum = "e665b8803e7b1d2a727f4023456bbbbe74da67099c585258af0ad9c5013b9b99"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -4829,7 +4830,7 @@ checksum = "728a70f3dbaf5bab7f0c4b1ac8d7ae5ea60a4b5549c8a5914361c99147a709d2"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -4872,15 +4873,15 @@ dependencies = [
 
 [[package]]
 name = "target-lexicon"
-version = "0.13.4"
+version = "0.13.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b1dd07eb858a2067e2f3c7155d54e929265c264e6f37efe3ee7a8d1b5a1dd0ba"
+checksum = "adb6935a6f5c20170eeceb1a3835a49e12e19d792f6dd344ccc76a985ca5a6ca"
 
 [[package]]
 name = "tempfile"
-version = "3.24.0"
+version = "3.25.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "655da9c7eb6305c55742045d5a8d2037996d61d8de95806335c7c86ce0f82e9c"
+checksum = "0136791f7c95b1f6dd99f9cc786b91bb81c3800b639b3478e561ddb7be95e5f1"
 dependencies = [
  "fastrand",
  "getrandom 0.3.4",
@@ -4924,7 +4925,7 @@ checksum = "a4558b58466b9ad7ca0f102865eccc95938dca1a74a856f2b57b6629050da261"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -4935,7 +4936,7 @@ checksum = "ebc4ee7f67670e9b64d05fa4253e753e016c6c95ff35b89b7941d6b856dec1d5"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -5055,7 +5056,7 @@ checksum = "af407857209536a95c8e56f8231ef2c2e2aff839b22e07a1ffcbc617e9db9fa5"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -5165,7 +5166,7 @@ checksum = "7490cfa5ec963746568740651ac6781f701c9c5ea257c58e057f3ba8cf69e8da"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -5374,6 +5375,7 @@ version = "0.1.0"
 dependencies = [
  "arbutil",
  "brotli",
+ "rkyv",
  "serde",
  "serde_json",
  "serde_with",
@@ -5525,7 +5527,7 @@ dependencies = [
  "bumpalo",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
  "wasm-bindgen-shared",
 ]
 
@@ -5616,7 +5618,7 @@ dependencies = [
  "leb128",
  "libc",
  "macho-unwind-info",
- "memmap2 0.9.9",
+ "memmap2 0.9.10",
  "more-asserts",
  "object 0.38.1",
  "rangemap",
@@ -5707,7 +5709,7 @@ dependencies = [
  "proc-macro-error2",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -5856,13 +5858,11 @@ dependencies = [
 
 [[package]]
 name = "which"
-version = "8.0.0"
+version = "8.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d3fabb953106c3c8eea8306e4393700d7657561cb43122571b172bbfb7c7ba1d"
+checksum = "81995fafaaaf6ae47a7d0cc83c67caf92aeb7e5331650ae6ff856f7c0c60c459"
 dependencies = [
- "env_home",
- "rustix",
- "winsafe",
+ "libc",
 ]
 
 [[package]]
@@ -6180,12 +6180,6 @@ dependencies = [
  "memchr",
 ]
 
-[[package]]
-name = "winsafe"
-version = "0.0.19"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d135d17ab770252ad95e9a872d365cf3090e3be864a34ab46f48555993efc904"
-
 [[package]]
 name = "wit-bindgen"
 version = "0.51.0"
@@ -6216,7 +6210,7 @@ dependencies = [
  "heck 0.5.0",
  "indexmap 2.13.0",
  "prettyplease",
- "syn 2.0.114",
+ "syn 2.0.117",
  "wasm-metadata",
  "wit-bindgen-core",
  "wit-component",
@@ -6232,7 +6226,7 @@ dependencies = [
  "prettyplease",
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
  "wit-bindgen-core",
  "wit-bindgen-rust",
 ]
@@ -6318,7 +6312,7 @@ checksum = "b659052874eb698efe5b9e8cf382204678a0086ebf46982b79d6ca3182927e5d"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
  "synstructure",
 ]
 
@@ -6339,7 +6333,7 @@ checksum = "88d2b8d9c68ad2b9e4340d7832716a4d21a22a1154777ad56ea55c51a9cf3831"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -6359,7 +6353,7 @@ checksum = "d71e5d6e06ab090c67b5e44993ec16b72dcbaabc526db883a360057678b48502"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
  "synstructure",
 ]
 
@@ -6380,7 +6374,7 @@ checksum = "ce36e65b0d2999d2aafac989fb249189a141aee1f53c612c1f37d72631959f69"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
 
 [[package]]
@@ -6413,5 +6407,5 @@ checksum = "eadce39539ca5cb3985590102671f2567e659fca9666581ad3411d59207951f3"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.114",
+ "syn 2.0.117",
 ]
```

### Cargo.toml
```diff
@@ -74,6 +74,7 @@ paste = { version = "1.0.15" }
 rand = { version = "0.8.4", default-features = false }
 rand_pcg = { version = "0.3.1", default-features = false }
 rayon = { version = "1.5.1" }
+rkyv = { version = "0.8.8" }
 reqwest = { version = "0.13.1" }
 ruint2 = { version = "1.9.0" }
 rustc-demangle = { version = "0.1.21" }
```

### arbos/programs/native.go
```diff
@@ -21,6 +21,7 @@ import "C"
 import (
 	"errors"
 	"fmt"
+	"sync/atomic"
 	"time"
 
 	"github.com/ethereum/go-ethereum/arbitrum/multigas"
@@ -49,6 +50,20 @@ type bytes32 = C.Bytes32
 type rustBytes = C.RustBytes
 type rustSlice = C.RustSlice
 
+// allowFallback controls whether compilation failures fall back to an alternative compiler.
+// Set once at startup via SetAllowFallback; defaults to true (fallback enabled).
+var allowFallback atomic.Bool
+
+func init() {
+	allowFallback.Store(true)
+}
+
+// SetAllowFallback configures whether to fall back to an alternative compiler on failure.
+func SetAllowFallback(enabled bool) {
+	allowFallback.Store(enabled)
+	log.Info("Compiler fallback for Stylus compilation configured", "enabled", enabled)
+}
+
 var (
 	stylusLRUCacheSizeBytesGauge    = metrics.NewRegisteredGauge("arb/arbos/stylus/cache/lru/size_bytes", nil)
 	stylusLRUCacheCountGauge        = metrics.NewRegisteredGauge("arb/arbos/stylus/cache/lru/count", nil)
@@ -226,8 +241,12 @@ func activateProgramInternal(
 				timeout := time.Second * 15
 				asm, err := compileNative(wasm, stylusVersion, debug, target, cranelift, timeout)
 				if err != nil {
-					log.Warn("initial stylus compilation failed", "address", addressForLogging, "cranelift", cranelift, "timeout", timeout, "err", err)
-					asm, err = compileNative(wasm, stylusVersion, debug, target, !cranelift, timeout)
+					if allowFallback.Load() {
+						log.Warn("initial stylus compilation failed, falling back to cranelift", "address", addressForLogging, "cranelift", cranelift, "timeout", timeout, "err", err)
+						asm, err = compileNative(wasm, stylusVersion, debug, target, !cranelift, timeout)
+					} else {
+						log.Warn("stylus compilation failed and fallback is disabled", "address", addressForLogging, "target", target, "timeout", timeout, "err", err)
+					}
 				}
 				results <- result{target, asm, err}
 			}
@@ -254,9 +273,10 @@ func activateProgramInternal(
 			"codehash", codehash,
 			"moduleHash", info.moduleHash,
 			"targets", targets,
+			"allowFallback", allowFallback.Load(),
 			"err", err,
 		)
-		panic(fmt.Sprintf("Compilation of %v failed for one or more targets despite activation succeeding: %v", addressForLogging, err))
+		panic(fmt.Sprintf("Compilation of %v failed for one or more targets despite activation succeeding (allowFallback=%v): %v", addressForLogging, allowFallback.Load(), err))
 	}
 	return info, asmMap, err
 }
```

### changelog/bragaigor-nit-4683.md
```diff
@@ -0,0 +1,2 @@
+### Configuration
+- Add `--execution.stylus-target.allow-fallback` flag: if true, fall back to an alternative compiler when compilation of a Stylus program fails (default: true).
```

### changelog/jco-machine-locator-fix.md
```diff
@@ -0,0 +1,2 @@
+### Fixed
+- Fix nil-dereference and log format in `cmd/nitro/nitro.go` when machine locator creation fails; return early instead of falling through to dereference nil locator
```

### changelog/pmikolajczyk-nit-4671.md
```diff
@@ -0,0 +1,3 @@
+### Internal
+- Introduce `ValidationInput` intermediate data structure with optional rkyv serialization in the validation crate
+- Minor refactor in JIT, prover and validator crates
\ No newline at end of file
```

### cmd/nitro/nitro.go
```diff
@@ -407,7 +407,7 @@ func mainImpl() int {
 	if nodeConfig.Node.ParentChainReader.Enable && nodeConfig.Validation.Wasm.EnableWasmrootsCheck {
 		err := checkWasmModuleRootCompatibility(ctx, nodeConfig.Validation.Wasm, l1Client, rollupAddrs)
 		if err != nil {
-			log.Warn("failed to check if node is compatible with on-chain WASM module root", "err", err)
+			log.Error("failed to check if node is compatible with on-chain WASM module root", "err", err)
 		}
 	}
 
@@ -416,7 +416,7 @@ func mainImpl() int {
 	if traceConfig.TracerName != "" {
 		tracer, err = tracers.LiveDirectory.New(traceConfig.TracerName, json.RawMessage(traceConfig.JSONConfig))
 		if err != nil {
-			log.Error("custom tracer error:", "name", traceConfig.TracerName, "err", err)
+			log.Error("custom tracer error", "name", traceConfig.TracerName, "err", err)
 			return 1
 		}
 		log.Info("enabling custom tracer", "name", traceConfig.TracerName)
@@ -452,6 +452,7 @@ func mainImpl() int {
 		deferFuncs = append(deferFuncs, func() { closeDb(consensusDB, "consensusDB") })
 	}
 	if err != nil {
+		log.Error("error opening consensus database", "err", err)
 		return 1
 	}
 
@@ -505,16 +506,17 @@ func mainImpl() int {
 			fatalErrChan,
 		)
 		if err != nil {
-			valNode = nil
-			log.Warn("couldn't init validation node", "err", err)
+			log.Error("couldn't init validation node", "err", err)
+			return 1
 		}
 	}
 
 	var wasmModuleRoot common.Hash
 	if liveNodeConfig.Get().Node.ValidatorRequired() {
 		locator, err := server_common.NewMachineLocator(liveNodeConfig.Get().Validation.Wasm.RootPath)
 		if err != nil {
-			log.Error("failed to create machine locator: %w", err)
+			log.Error("failed to create machine locator", "err", err)
+			return 1
 		}
 		wasmModuleRoot = locator.LatestWasmModuleRoot()
 	}
```

### crates/arbutil/Cargo.toml
```diff
@@ -13,7 +13,7 @@ rust-version.workspace = true
 digest = { workspace = true }
 eyre = { workspace = true }
 fnv = { workspace = true }
-hex = { workspace = true }
+hex = { workspace = true, features = ["alloc"] }
 num_enum = { workspace = true, default-features = true }
 num-traits = { workspace = true }
 ruint2 = { workspace = true }
```

### crates/caller-env/src/wasip1_stub.rs
```diff
@@ -10,7 +10,7 @@
 use crate::{ExecEnv, GuestPtr, MemAccess};
 
 #[repr(transparent)]
-pub struct Errno(pub(crate) u16);
+pub struct Errno(pub u16);
 
 pub const ERRNO_SUCCESS: Errno = Errno(0);
 pub const ERRNO_BADF: Errno = Errno(8);
```

### crates/jit/src/caller_env.rs
```diff
@@ -135,45 +135,45 @@ impl ExecEnv for JitExecEnv<'_> {
 
 impl WavmIo for WasmEnv {
     fn get_u64_global(&self, idx: usize) -> Option<u64> {
-        self.small_globals.get(idx).copied()
+        self.input.small_globals.get(idx).copied()
     }
 
     fn set_u64_global(&mut self, idx: usize, val: u64) -> bool {
-        let Some(g) = self.small_globals.get_mut(idx) else {
+        let Some(g) = self.input.small_globals.get_mut(idx) else {
             return false;
         };
         *g = val;
         true
     }
 
     fn get_bytes32_global(&self, idx: usize) -> Option<&[u8; 32]> {
-        self.large_globals.get(idx).map(|b| &b.0)
+        self.input.large_globals.get(idx)
     }
 
     fn set_bytes32_global(&mut self, idx: usize, val: [u8; 32]) -> bool {
-        let Some(g) = self.large_globals.get_mut(idx) else {
+        let Some(g) = self.input.large_globals.get_mut(idx) else {
             return false;
         };
-        *g = val.into();
+        *g = val;
         true
     }
 
     fn get_sequencer_message(&self, num: u64) -> Option<&[u8]> {
-        self.sequencer_messages.get(&num).map(|v| v.as_slice())
+        self.input
+            .sequencer_messages
+            .get(&num)
+            .map(|v| v.as_slice())
     }
 
     fn get_delayed_message(&self, num: u64) -> Option<&[u8]> {
-        self.delayed_messages.get(&num).map(|v| v.as_slice())
+        self.input.delayed_messages.get(&num).map(|v| v.as_slice())
     }
 
     fn get_preimage(&self, preimage_type: u8, hash: &[u8; 32]) -> Option<&[u8]> {
-        let Ok(pt) = preimage_type.try_into() else {
-            eprintln!("Go trying to get a preimage with unknown type {preimage_type}");
-            return None;
-        };
-        self.preimages
-            .get(&pt)
-            .and_then(|m| m.get(&Bytes32(*hash)))
+        self.input
+            .preimages
+            .get(&preimage_type)
+            .and_then(|m| m.get(hash))
             .map(|v| v.as_slice())
     }
 }
```

### crates/jit/src/lib.rs
```diff
@@ -2,21 +2,18 @@
 // For license information, see https://github.com/OffchainLabs/nitro/blob/master/LICENSE.md
 
 use crate::machine::Escape;
-use arbutil::{Bytes32, PreimageType};
+use arbutil::Bytes32;
 use clap::{Args, Parser, Subcommand};
-use std::collections::HashMap;
 use std::io::BufWriter;
 use std::net::TcpStream;
 use std::path::PathBuf;
 use std::time::Duration;
-use validation::{BatchInfo, UserWasm};
 use wasmer::{FrameInfo, FunctionEnv, Instance, Pages, Store};
 
 mod arbcompress;
 mod arbcrypto;
 mod caller_env;
 pub mod machine;
-mod prepare;
 pub mod program;
 pub mod stylus_backend;
 mod test;
@@ -63,7 +60,7 @@ pub enum InputMode {
     Local(LocalInput),
     /// Use direct Rust objects
     #[command(skip)]
-    Native(NativeInput),
+    Native(validation::ValidationInput),
     /// Continuously read new inputs from TCP connections
     Continuous,
 }
@@ -116,15 +113,6 @@ impl From<GlobalState> for validation::GoGlobalState {
     }
 }
 
-#[derive(Clone, Debug)]
-pub struct NativeInput {
-    pub old_state: GlobalState,
-    pub inbox: Vec<BatchInfo>,
-    pub delayed_inbox: Vec<BatchInfo>,
-    pub preimages: HashMap<PreimageType, HashMap<Bytes32, Vec<u8>>>,
-    pub programs: HashMap<Bytes32, UserWasm>,
-}
-
 /// Result of running the JIT validation.
 pub struct RunResult {
     /// Amount of memory used by the Wasm instance.
@@ -176,10 +164,10 @@ fn run_instance(
         memory_used,
         runtime: env.process.timestamp.elapsed(),
         new_state: GlobalState {
-            last_block_hash: env.large_globals[0],
-            last_send_root: env.large_globals[1],
-            inbox_position: env.small_globals[0],
-            position_within_message: env.small_globals[1],
+            last_block_hash: Bytes32(env.input.large_globals[0]),
+            last_send_root: Bytes32(env.input.large_globals[1]),
+            inbox_position: env.input.small_globals[0],
+            position_within_message: env.input.small_globals[1],
         },
         error: None,
         trace: vec![],
```

### crates/jit/src/machine.rs
```diff
@@ -2,16 +2,14 @@
 // For license information, see https://github.com/OffchainLabs/nitro/blob/master/LICENSE.md
 
 use crate::{
-    arbcompress, arbcrypto, prepare::prepare_env_from_json, program,
-    stylus_backend::CothreadHandler, wasip1_stub, wavmio, InputMode, LocalInput, NativeInput, Opts,
-    ValidatorOpts,
+    arbcompress, arbcrypto, program, stylus_backend::CothreadHandler, wasip1_stub, wavmio,
+    InputMode, LocalInput, Opts, ValidatorOpts,
 };
 use arbutil::{Bytes32, PreimageType};
 use caller_env::GoRuntimeState;
 use eyre::{bail, ErrReport, Report, Result};
 use sha3::{Digest, Keccak256};
 use std::{
-    collections::BTreeMap,
     collections::HashMap,
     fs::File,
     io::{self, BufReader, BufWriter, ErrorKind, Read},
@@ -20,7 +18,7 @@ use std::{
     time::Instant,
 };
 use thiserror::Error;
-use validation::BatchInfo;
+use validation::local_target;
 use wasmer::sys::CompilerConfig;
 use wasmer::{
     imports, Engine, Function, FunctionEnv, FunctionEnvMut, Instance, Memory, Module, RuntimeError,
@@ -238,8 +236,6 @@ impl From<RuntimeError> for Escape {
 }
 
 pub type WasmEnvMut<'a> = FunctionEnvMut<'a, WasmEnv>;
-pub type Inbox = BTreeMap<u64, Vec<u8>>;
-pub type Preimages = BTreeMap<PreimageType, BTreeMap<Bytes32, Vec<u8>>>;
 pub type ModuleAsm = Arc<[u8]>;
 
 #[derive(Default)]
@@ -248,18 +244,12 @@ pub struct WasmEnv {
     pub memory: Option<Memory>,
     /// Go's general runtime state
     pub go_state: GoRuntimeState,
-    /// An ordered list of the 8-byte globals
-    pub small_globals: [u64; 2],
-    /// An ordered list of the 32-byte globals
-    pub large_globals: [Bytes32; 2],
-    /// An oracle allowing the prover to reverse keccak256
-    pub preimages: Preimages,
-    /// A collection of programs called during the course of execution
+    /// Validation input (globals, inbox, preimages). Note: module_asms is drained
+    /// into the `module_asms` field below during loading, so it will be empty at runtime.
+    pub input: validation::ValidationInput,
+    /// Arc-wrapped module assemblies, drained from `input.module_asms` to allow
+    /// cheap cloning when passing modules to stylus program threads.
     pub module_asms: HashMap<Bytes32, ModuleAsm>,
-    /// The sequencer inbox's messages
-    pub sequencer_messages: Inbox,
-    /// The delayed inbox's messages
-    pub delayed_messages: Inbox,
     /// The purpose and connections of this process
     pub process: ProcessEnv,
     // threads
@@ -274,21 +264,32 @@ impl TryFrom<&Opts> for WasmEnv {
         env.process.debug = opts.validator.debug;
 
         match &opts.input_mode {
-            InputMode::Json { inputs } => prepare_env_from_json(inputs, opts.validator.debug),
-            InputMode::Local(local) => prepare_env_from_files(env, local),
-            InputMode::Native(native) => prepare_env_from_native(env, native),
-            InputMode::Continuous => Ok(env),
+            InputMode::Json { inputs } => {
+                let file = File::open(inputs)?;
+                let req = validation::ValidationRequest::from_reader(BufReader::new(file))?;
+                let input = validation::ValidationInput::from_request(&req, local_target())
+                    .map_err(|e| eyre::eyre!(e))?;
+                load_validation_input(&mut env, input);
+            }
+            InputMode::Local(local) => prepare_env_from_files(&mut env, local)?,
+            InputMode::Native(vi) => load_validation_input(&mut env, vi.clone()),
+            InputMode::Continuous => {}
         }
+        Ok(env)
     }
 }
 
-fn prepare_env_from_files(env: WasmEnv, input: &LocalInput) -> Result<WasmEnv> {
-    let mut native = NativeInput {
-        old_state: input.old_state.clone(),
-        inbox: vec![],
-        delayed_inbox: vec![],
-        preimages: HashMap::new(),
-        programs: HashMap::new(),
+fn prepare_env_from_files(env: &mut WasmEnv, input: &LocalInput) -> Result<()> {
+    let mut vi = validation::ValidationInput {
+        small_globals: [
+            input.old_state.inbox_position,
+            input.old_state.position_within_message,
+        ],
+        large_globals: [
+            input.old_state.last_block_hash.0,
+            input.old_state.last_send_root.0,
+        ],
+        ..Default::default()
     };
 
     let mut inbox_position = input.old_state.inbox_position;
@@ -297,19 +298,13 @@ fn prepare_env_from_files(env: WasmEnv, input: &LocalInput) -> Result<WasmEnv> {
     for path in &input.inbox {
         let mut msg = vec![];
         File::open(path)?.read_to_end(&mut msg)?;
-        native.inbox.push(BatchInfo {
-            number: inbox_position,
-            data: msg,
-        });
+        vi.sequencer_messages.insert(inbox_position, msg);
         inbox_position += 1;
     }
     for path in &input.delayed_inbox {
         let mut msg = vec![];
         File::open(path)?.read_to_end(&mut msg)?;
-        native.delayed_inbox.push(BatchInfo {
-            number: delayed_position,
-            data: msg,
-        });
+        vi.delayed_messages.insert(delayed_position, msg);
         delayed_position += 1;
     }
 
@@ -329,7 +324,10 @@ fn prepare_env_from_files(env: WasmEnv, input: &LocalInput) -> Result<WasmEnv> {
             file.read_exact(&mut buf)?;
             preimages.push(buf);
         }
-        let keccak_preimages = native.preimages.entry(PreimageType::Keccak256).or_default();
+        let keccak_preimages = vi
+            .preimages
+            .entry(PreimageType::Keccak256 as u8)
+            .or_default();
         for preimage in preimages {
             let mut hasher = Keccak256::new();
             hasher.update(&preimage);
@@ -338,39 +336,18 @@ fn prepare_env_from_files(env: WasmEnv, input: &LocalInput) -> Result<WasmEnv> {
         }
     }
 
-    prepare_env_from_native(env, &native)
+    load_validation_input(env, vi);
+    Ok(())
 }
 
-fn prepare_env_from_native(mut env: WasmEnv, input: &NativeInput) -> Result<WasmEnv> {
+pub(crate) fn load_validation_input(env: &mut WasmEnv, mut input: validation::ValidationInput) {
     env.process.already_has_input = true;
-
-    for msg in &input.inbox {
-        env.sequencer_messages.insert(msg.number, msg.data.clone());
-    }
-    for msg in &input.delayed_inbox {
-        env.delayed_messages.insert(msg.number, msg.data.clone());
+    let module_asms = std::mem::take(&mut input.module_asms);
+    for (module_hash, module_asm) in module_asms {
+        env.module_asms
+            .insert(Bytes32(module_hash), module_asm.into());
     }
-
-    for (preimage_type, preimages_map) in &input.preimages {
-        let type_map = env.preimages.entry(*preimage_type).or_default();
-        for (hash, preimage) in preimages_map {
-            type_map.insert(*hash, preimage.clone());
-        }
-    }
-
-    for (hash, program) in &input.programs {
-        env.module_asms.insert(*hash, program.as_ref().into());
-    }
-
-    env.small_globals = [
-        input.old_state.inbox_position,
-        input.old_state.position_within_message,
-    ];
-    env.large_globals = [
-        input.old_state.last_block_hash,
-        input.old_state.last_send_root,
-    ];
-    Ok(env)
+    env.input = input;
 }
 
 pub struct ProcessEnv {
```
