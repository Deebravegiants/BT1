# [?] Fix non-deterministic build (use paste! instead of gensym!) (#1328)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2022-03-01
Source: https://github.com/moonbeam-foundation/moonbeam/commit/13b59ffd03902fa71333cb13455c8f01f8826ba1
Type: security-commit

## Details
Fix non-deterministic build (use paste! instead of gensym!) (#1328)

* use paste! instead of gensym! for Balances precompile impl

* fix typo

Co-authored-by: Éloïs <c@elo.tf>

Co-authored-by: Éloïs <c@elo.tf>

## Patch
### Cargo.lock
```diff
@@ -200,8 +200,8 @@ version = "1.1.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a3203e79f4dd9bdda415ed03cf14dae5a2bf775c683a00f94e9cd1faf0f596e5"
 dependencies = [
- "quote 1.0.15",
- "syn 1.0.86",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -354,9 +354,9 @@ version = "0.1.52"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "061a7acccaa286c011ddc30970520b98fa40e00c9d644633fb26b5fc63a265e3"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -418,9 +418,9 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7862e21c893d65a1650125d157eaeec691439379a1cee17ee49031b79236ada4"
 dependencies = [
  "proc-macro-error",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -587,8 +587,8 @@ dependencies = [
  "lazy_static",
  "lazycell",
  "peeking_take_while",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
+ "proc-macro2",
+ "quote",
  "regex",
  "rustc-hash",
  "shlex",
@@ -1159,9 +1159,9 @@ checksum = "01d42c94ce7c2252681b5fed4d3627cc807b13dfc033246bd05d5b252399000e"
 dependencies = [
  "heck 0.4.0",
  "proc-macro-error",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -1182,9 +1182,9 @@ version = "0.4.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "efe942512e068e15991cbcef4e8182884555febbb21b5b4faf5dd5561850141a"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -1529,8 +1529,8 @@ version = "0.1.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5e98e2ad1a782e33928b96fc3948e7c355e5af34ba4de7670fe8bac2a3b2006d"
 dependencies = [
- "quote 1.0.15",
- "syn 1.0.86",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -1764,9 +1764,9 @@ version = "0.1.0"
 source = "git+https://github.com/purestake/cumulus?branch=moonbeam-polkadot-v0.9.17#b43fcfff1df6bad837b98e5862e60367b9bc92e0"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -2002,7 +2002,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a5bbed42daaa95e780b60a50546aa345b8413a1e46f9a40a12907d3598f038db"
 dependencies = [
  "data-encoding",
- "syn 1.0.86",
+ "syn",
 ]
 
 [[package]]
@@ -2011,9 +2011,9 @@ version = "2.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fcc3dd5e9e9c0b295d6e1e4d811fb6f157d5ffd784b8d202fc62eac8035a770b"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -2023,10 +2023,10 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4fb810d30a7c1953f91334de7244731fc3f3c10d7fe163338a35b9f640960321"
 dependencies = [
  "convert_case",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
+ "proc-macro2",
+ "quote",
  "rustc_version 0.4.0",
- "syn 1.0.86",
+ "syn",
 ]
 
 [[package]]
@@ -2148,9 +2148,9 @@ version = "0.9.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "558e40ea573c374cf53507fd240b7ee2f5477df7cfebdb97323ec61c719399c5"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -2201,9 +2201,9 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7c5f0096a91d210159eceb2ff5e1c4da18388a170e1e3ce948aac9c8fdbbf595"
 dependencies = [
  "heck 0.3.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -2221,9 +2221,9 @@ version = "0.6.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "946ee94e3dbf58fdd324f9ce245c7b238d46a66f00e86a020b71996349e46cce"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -2232,9 +2232,9 @@ version = "0.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4e58b112d5099aa0857c5d05f0eacab86406dd8c0f85fe5d320a13256d29ecf4"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -2874,9 +2874,9 @@ source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0
 dependencies = [
  "Inflector",
  "frame-support-procedural-tools",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -2886,19 +2886,19 @@ source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0
 dependencies = [
  "frame-support-procedural-tools-derive",
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
 name = "frame-support-procedural-tools-derive"
 version = "3.0.0"
 source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0.9.17#c84f20046004e0c5f158d36bf9c8b2ecfdc41281"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -3085,9 +3085,9 @@ version = "0.3.21"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "33c1e13800337f4d4d7a316bf45a567dbcb6ffe087f16424852d97e97a91f512"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -3163,18 +3163,6 @@ dependencies = [
  "version_check",
 ]
 
-[[package]]
-name = "gensym"
-version = "0.1.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fcb328fe25cbf075818a3e57bb5ee39b49b4f26c94d685356426154c5962cccd"
-dependencies = [
- "proc-macro2 0.4.30",
- "quote 0.6.13",
- "syn 0.15.44",
- "uuid",
-]
-
 [[package]]
 name = "getrandom"
 version = "0.1.16"
@@ -3610,9 +3598,9 @@ version = "0.2.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "11d7a9f6330b71fea57921c9b61c47ee6e84f72d394754eff6163ae67e7395eb"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -3779,9 +3767,9 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5b939a78fa820cdfcb7ee7484466746a7377760970f6f9c6fe19f9edcc8a38d2"
 dependencies = [
  "proc-macro-crate 0.1.5",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -3937,9 +3925,9 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4299ebf790ea9de1cb72e73ff2ae44c723ef264299e5e2d5ef46a371eb3ac3d8"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -4621,8 +4609,8 @@ version = "0.25.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "072c290f727d39bdc4e9d6d1c847978693d25a673bd757813681e33e5f6c00c2"
 dependencies = [
- "quote 1.0.15",
- "syn 1.0.86",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -6069,9 +6057,9 @@ checksum = "424f6e86263cd5294cbd7f1e95746b95aca0e0d66bff31e5a40d6baa87b4aa99"
 dependencies = [
  "proc-macro-crate 1.1.3",
  "proc-macro-error",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
  "synstructure",
 ]
 
@@ -6119,9 +6107,9 @@ version = "0.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "01fcc0b8149b4632adc89ac3b7b31a12fb6099a0317a4eb2ebff574ef7de7218"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -6375,9 +6363,9 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "486ea01961c4a818096de679a8b740b26d9033146ac5291b1c98557658f8cdd9"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -6427,9 +6415,9 @@ version = "0.1.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a15c83b586f00268c619c1cb3340ec1a6f59dd9ba1d9833a273a68e6d5cd8ffc"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -7089,13 +7077,13 @@ dependencies = [
  "fp-evm",
  "frame-support",
  "frame-system",
- "gensym",
  "log",
  "num_enum",
  "pallet-balances",
  "pallet-evm",
  "pallet-timestamp",
  "parity-scale-codec",
+ "paste",
  "precompile-utils",
  "scale-info",
  "serde",
@@ -7550,9 +7538,9 @@ version = "4.0.0-dev"
 source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0.9.17#c84f20046004e0c5f158d36bf9c8b2ecfdc41281"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -7822,9 +7810,9 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1557010476e0595c9b568d16dcfb81b93cdeb157612726f5170d31aa707bed27"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -7871,8 +7859,8 @@ version = "0.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f557c32c6d268a07c921471619c0295f5efad3a0e76d4f97a05c091a51d110b2"
 dependencies = [
- "proc-macro2 1.0.36",
- "syn 1.0.86",
+ "proc-macro2",
+ "syn",
  "synstructure",
 ]
 
@@ -8152,9 +8140,9 @@ checksum = "99b8db626e31e5b81787b9783425769681b347011cc59471e33ea46d2ea0cf55"
 dependencies = [
  "pest",
  "pest_meta",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -8202,9 +8190,9 @@ version = "0.4.29"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "044964427019eed9d49d9d5bbce6047ef18f37100ea400912a9fa4a3523ab12a"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -8213,9 +8201,9 @@ version = "1.0.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "744b6f092ba29c3650faf274db506afd39944f48420f6c86b17cfe0ee1cb36bb"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -8931,9 +8919,9 @@ version = "0.9.17"
 source = "git+https://github.com/purestake/polkadot?branch=moonbeam-polkadot-v0.9.17#66cb46bb3a7bd7295d1eb39a391559bc6efb2a22"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -8964,7 +8952,7 @@ dependencies = [
  "polkadot-erasure-coding",
  "polkadot-node-core-pvf",
  "polkadot-node-primitives",
- "quote 1.0.15",
+ "quote",
  "thiserror",
 ]
 
@@ -9418,10 +9406,10 @@ name = "precompile-utils-macro"
 version = "0.1.0"
 dependencies = [
  "num_enum",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
+ "proc-macro2",
+ "quote",
  "sha3 0.8.2",
- "syn 1.0.86",
+ "syn",
 ]
 
 [[package]]
@@ -9490,9 +9478,9 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "da25490ff9892aab3fcf7c36f08cfb902dd3e71ca0f9f9517bea02a73a5ce38c"
 dependencies = [
  "proc-macro-error-attr",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
  "version_check",
 ]
 
@@ -9502,27 +9490,18 @@ version = "1.0.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a1be40180e52ecc98ad80b184934baf3d0d29f979574e439af5a55274b35f869"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
+ "proc-macro2",
+ "quote",
  "version_check",
 ]
 
-[[package]]
-name = "proc-macro2"
-version = "0.4.30"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cf3d2011ab5c909338f7887f4fc896d35932e29146c12c8d01da6b22a80ba759"
-dependencies = [
- "unicode-xid 0.1.0",
-]
-
 [[package]]
 name = "proc-macro2"
 version = "1.0.36"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c7342d5883fbccae1cc37a2353b09c87c9b0f3afd73f5fb9bba687a1f733b029"
 dependencies = [
- "unicode-xid 0.2.2",
+ "unicode-xid",
 ]
 
 [[package]]
@@ -9577,9 +9556,9 @@ checksum = "f9cc1a3263e07e0bf68e96268f37665207b49560d98739662cdfaae215c720fe"
 dependencies = [
  "anyhow",
  "itertools",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -9643,22 +9622,13 @@ dependencies = [
  "pin-project-lite 0.1.12",
 ]
 
-[[package]]
-name = "quote"
-version = "0.6.13"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6ce23b6b870e8f94f81fb0a363d65d86675884b34a09043c81e5562f11c1f8e1"
-dependencies = [
- "proc-macro2 0.4.30",
-]
-
 [[package]]
 name = "quote"
 version = "1.0.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "864d3e96a899863136fc6e99f3d7cae289dafe43bf2c5ac19b70df7210c0a145"
 dependencies = [
- "proc-macro2 1.0.36",
+ "proc-macro2",
 ]
 
 [[package]]
@@ -9972,9 +9942,9 @@ version = "1.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4c38e3aecd2b21cb3959637b883bb3714bc7e43f0268b9a29d3743ee3e55cdd2"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -10137,9 +10107,9 @@ version = "0.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e33d7b2abe0c340d8797fe2907d3f20d3b5ea5908683618bfe80df7f621f672a"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -10537,9 +10507,9 @@ version = "4.0.0-dev"
 source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0.9.17#c84f20046004e0c5f158d36bf9c8b2ecfdc41281"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -11355,9 +11325,9 @@ version = "4.0.0-dev"
 source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0.9.17#c84f20046004e0c5f158d36bf9c8b2ecfdc41281"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -11433,9 +11403,9 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "baeb2780690380592f86205aa4ee49815feb2acad8c2f59e6dd207148c3f1fcd"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -11602,9 +11572,9 @@ version = "1.0.136"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "08597e7152fcd306f41838ed3e37be9eaeed2b61c42e2117266a554fab4662f9"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -11799,9 +11769,9 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f2086e458a369cdca838e9f6ed04b4cc2e3ce636d99abb80c9e2eada107749cf"
 dependencies = [
  "faster-hex",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -11925,9 +11895,9 @@ source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0
 dependencies = [
  "blake2-rfc",
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -12163,10 +12133,10 @@ name = "sp-core-hashing-proc-macro"
 version = "4.0.0-dev"
 source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0.9.17#c84f20046004e0c5f158d36bf9c8b2ecfdc41281"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
+ "proc-macro2",
+ "quote",
  "sp-core-hashing",
- "syn 1.0.86",
+ "syn",
 ]
 
 [[package]]
@@ -12183,9 +12153,9 @@ name = "sp-debug-derive"
 version = "4.0.0"
 source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0.9.17#c84f20046004e0c5f158d36bf9c8b2ecfdc41281"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -12313,9 +12283,9 @@ version = "4.0.0-dev"
 source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0.9.17#c84f20046004e0c5f158d36bf9c8b2ecfdc41281"
 dependencies = [
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -12394,9 +12364,9 @@ source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0
 dependencies = [
  "Inflector",
  "proc-macro-crate 1.1.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -12578,9 +12548,9 @@ version = "4.0.0-dev"
 source = "git+https://github.com/purestake/substrate?branch=moonbeam-polkadot-v0.9.17#c84f20046004e0c5f158d36bf9c8b2ecfdc41281"
 dependencies = [
  "parity-scale-codec",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -12618,11 +12588,11 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8319f44e20b42e5c11b88b1ad4130c35fe2974665a007b08b02322070177136a"
 dependencies = [
  "Inflector",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
+ "proc-macro2",
+ "quote",
  "serde",
  "serde_json",
- "unicode-xid 0.2.2",
+ "unicode-xid",
 ]
 
 [[package]]
@@ -12657,9 +12627,9 @@ checksum = "f2261c91034a1edc3fc4d1b80e89d82714faede0515c14a75da10cb941546bbf"
 dependencies = [
  "cfg_aliases",
  "memchr",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -12706,9 +12676,9 @@ checksum = "dcb5ae327f9cc13b68763b5749770cb9e048a99bd9dfdfa58d0cf05d5f64afe0"
 dependencies = [
  "heck 0.3.3",
  "proc-macro-error",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -12727,10 +12697,10 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5bb0dc7ee9c15cea6199cde9a127fa16a4c5819af85395457ad72d68edc85a38"
 dependencies = [
  "heck 0.3.3",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
+ "proc-macro2",
+ "quote",
  "rustversion",
- "syn 1.0.86",
+ "syn",
 ]
 
 [[package]]
@@ -12927,26 +12897,15 @@ version = "2.4.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6bdef32e8150c2a081110b42772ffe7d7c9032b606bc226c8260fd97e0976601"
 
-[[package]]
-name = "syn"
-version = "0.15.44"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9ca4b3b69a77cbe1ffc9e198781b7acb0c7365a883670e8f1c1bc66fba79a5c5"
-dependencies = [
- "proc-macro2 0.4.30",
- "quote 0.6.13",
- "unicode-xid 0.1.0",
-]
-
 [[package]]
 name = "syn"
 version = "1.0.86"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8a65b3f4ffa0092e9887669db0eae07941f023991ab58ea44da8fe8e2d511c6b"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "unicode-xid 0.2.2",
+ "proc-macro2",
+ "quote",
+ "unicode-xid",
 ]
 
 [[package]]
@@ -12955,10 +12914,10 @@ version = "0.12.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "474aaa926faa1603c40b7885a9eaea29b444d1cb2850cb7c0e37bb1a4182f4fa"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
- "unicode-xid 0.2.2",
+ "proc-macro2",
+ "quote",
+ "syn",
+ "unicode-xid",
 ]
 
 [[package]]
@@ -13036,9 +12995,9 @@ version = "1.0.30"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "aa32fd3f627f367fe16f893e2597ae3c05020f8bba2666a4e6ea73d377e5714b"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -13163,9 +13122,9 @@ version = "1.7.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b557f72f448c511a979e2564e55d74e6c4432fc96ff4f6241bc6bded342643b7"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -13249,9 +13208,9 @@ version = "0.1.19"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8276d9a4a3a558d7b7ad5303ad50b53d58264641b82914b7ada36bd762e7a716"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -13525,12 +13484,6 @@ version = "0.1.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9337591893a19b88d8d87f2cec1e73fad5cdfd10e5a6f349f498ad6ea2ffb1e3"
 
-[[package]]
-name = "unicode-xid"
-version = "0.1.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fc72304796d0818e357ead4e000d19c9c174ab23dc11093ac919054d20a6a7fc"
-
 [[package]]
 name = "unicode-xid"
 version = "0.2.2"
@@ -13606,15 +13559,6 @@ dependencies = [
  "percent-encoding 2.1.0",
 ]
 
-[[package]]
-name = "uuid"
-version = "0.7.4"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "90dbc611eb48397705a6b0f6e917da23ae517e4d127123d2cf7674206627d32a"
-dependencies = [
- "rand 0.6.5",
-]
-
 [[package]]
 name = "valuable"
 version = "0.1.0"
@@ -13722,9 +13666,9 @@ dependencies = [
  "bumpalo",
  "lazy_static",
  "log",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
  "wasm-bindgen-shared",
 ]
 
@@ -13746,7 +13690,7 @@ version = "0.2.74"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "088169ca61430fe1e58b8096c24975251700e7b1f6fd91cc9d59b04fb9b18bd4"
 dependencies = [
- "quote 1.0.15",
+ "quote",
  "wasm-bindgen-macro-support",
 ]
 
@@ -13756,9 +13700,9 @@ version = "0.2.74"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "be2241542ff3d9f241f5e2cb6dd09b37efe786df8851c54957683a49f0987a97"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
  "wasm-bindgen-backend",
  "wasm-bindgen-shared",
 ]
@@ -14349,9 +14293,9 @@ version = "0.1.0"
 source = "git+https://github.com/purestake/polkadot?branch=moonbeam-polkadot-v0.9.17#66cb46bb3a7bd7295d1eb39a391559bc6efb2a22"
 dependencies = [
  "Inflector",
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
 ]
 
 [[package]]
@@ -14491,9 +14435,9 @@ version = "1.3.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "81e8f13fef10b63c06356d65d416b070798ddabcadc10d3ece0c5be9b3c7eddb"
 dependencies = [
- "proc-macro2 1.0.36",
- "quote 1.0.15",
- "syn 1.0.86",
+ "proc-macro2",
+ "quote",
+ "syn",
  "synstructure",
 ]
 
```

### precompiles/balances-erc20/Cargo.toml
```diff
@@ -6,9 +6,9 @@ edition = "2018"
 version = "0.1.0"
 
 [dependencies]
-gensym = "0.1.0"
 log = "0.4"
 num_enum = { version = "0.5.3", default-features = false }
+paste = "1.0.6"
 slices = "0.2.0"
 
 # Moonbeam
```

### precompiles/balances-erc20/src/lib.rs
```diff
@@ -69,35 +69,35 @@ pub trait InstanceToPrefix {
 
 // We use a macro to implement the trait for () and the 16 substrate Instance.
 macro_rules! impl_prefix {
-	($instance:ty, $name:literal) => {
-		// Generate unique UUID to have unique module names.
-		gensym::gensym! { _impl_prefix!{ $instance, $name }}
-	};
-}
-
-macro_rules! _impl_prefix {
-	($module:ident, $instance:ty, $name:literal) => {
-		mod $module {
-			use super::*;
+	($instance:ident, $name:literal) => {
+		// Using `paste!` we generate a dedicated module to avoid collisions
+		// between each instance `Approves` struct.
+		paste::paste! {
+			mod [<_impl_prefix_ $instance:snake>] {
+				use super::*;
 
-			pub struct Approves;
+				pub struct Approves;
 
-			impl StorageInstance for Approves {
-				const STORAGE_PREFIX: &'static str = "Approves";
+				impl StorageInstance for Approves {
+					const STORAGE_PREFIX: &'static str = "Approves";
 
-				fn pallet_prefix() -> &'static str {
-					$name
+					fn pallet_prefix() -> &'static str {
+						$name
+					}
 				}
-			}
 
-			impl InstanceToPrefix for $instance {
-				type ApprovesPrefix = Approves;
+				impl InstanceToPrefix for $instance {
+					type ApprovesPrefix = Approves;
+				}
 			}
 		}
 	};
 }
 
-impl_prefix!((), "Erc20Instance0Balances");
+// Since the macro expect a `ident` to be used with `paste!` we cannot provide `()` directly.
+type Instance0 = ();
+
+impl_prefix!(Instance0, "Erc20Instance0Balances");
 impl_prefix!(Instance1, "Erc20Instance1Balances");
 impl_prefix!(Instance2, "Erc20Instance2Balances");
 impl_prefix!(Instance3, "Erc20Instance3Balances");
```
