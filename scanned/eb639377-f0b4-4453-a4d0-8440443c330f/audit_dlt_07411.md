# [?] chore: bump alloy and remove RUSTSEC-2024-0437 (#12995)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-01-09
Source: https://github.com/foundry-rs/foundry/commit/e589ccfc404f878b77c1e6a5ea85023ad99482b6
Type: security-commit

## Details
chore: bump alloy and remove RUSTSEC-2024-0437 (#12995)

* chore: remove RUSTSEC-2024-0437

* chore: bump release deps

* chore: fmt

* chore: remove lru advisory

* chore: add lru advisory

* chore: bump ratatui to remove lru ignore rustsec

---------

Co-authored-by: Matthias Seitz <matthias.seitz@outlook.de>

## Patch
### Cargo.lock
```diff
@@ -74,14 +74,14 @@ dependencies = [
  "alloy-primitives",
  "num_enum",
  "serde",
- "strum 0.27.2",
+ "strum",
 ]
 
 [[package]]
 name = "alloy-consensus"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f3dcd2b4e208ce5477de90ccdcbd4bde2c8fb06af49a443974e92bb8f2c5e93f"
+checksum = "8e30ab0d3e3c32976f67fc1a96179989e45a69594af42003a6663332f9b0bb9d"
 dependencies = [
  "alloy-eips",
  "alloy-primitives",
@@ -106,9 +106,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-consensus-any"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ee5655f234985f5ab1e31bef7e02ed11f0a899468cf3300e061e1b96e9e11de0"
+checksum = "c20736b1f9d927d875d8777ef0c2250d4c57ea828529a9dbfa2c628db57b911e"
 dependencies = [
  "alloy-consensus",
  "alloy-eips",
@@ -120,9 +120,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-contract"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7f01b6d8e5b4f3222aaf7f18613a7292e2fbc9163fe120649cd1b078ca534349"
+checksum = "008aba161fce2a0d94956ae09d7d7a09f8fbdf18acbef921809ef126d6cdaf97"
 dependencies = [
  "alloy-consensus",
  "alloy-dyn-abi",
@@ -187,9 +187,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-eip5792"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cdb31eba85ca1ac2f9df9170ffda56b470816b899c8be577a5b4c6a830368682"
+checksum = "18b245b59ee8909e9e7ee7bfabce07ea61bdfdc9de101bd95c431109320c17ec"
 dependencies = [
  "alloy-primitives",
  "alloy-serde",
@@ -213,9 +213,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-eips"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6847d641141b92a1557094aa6c236cbe49c06fb24144d4a21fe6acb970c15888"
+checksum = "15b85157b7be31fc4adf6acfefcb0d4308cba5dbd7a8d8e62bcc02ff37d6131a"
 dependencies = [
  "alloy-eip2124",
  "alloy-eip2930",
@@ -238,9 +238,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-ens"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9ddbb0d31df814ea588fc61034c3f3d21dc3678e65e26a50fff21fd35b4d0d3b"
+checksum = "39f417fd85d875363989f8ba4e70a15d7fd0f766c8296f3f6b0f22dbc86ee5b4"
 dependencies = [
  "alloy-contract",
  "alloy-primitives",
@@ -274,9 +274,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-genesis"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fe3192fca2eb0b0c4b122b3c2d8254496b88a4e810558dddd3ea2f30ad9469df"
+checksum = "a838301c4e2546c96db1848f18ffe9f722f2fccd9715b83d4bf269a2cf00b5a1"
 dependencies = [
  "alloy-eips",
  "alloy-primitives",
@@ -314,9 +314,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-json-rpc"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d4ab3330e491053e9608b2a315f147357bb8acb9377a988c1203f2e8e2b296c9"
+checksum = "60f045b69b5e80b8944b25afe74ae6b974f3044d84b4a7a113da04745b2524cc"
 dependencies = [
  "alloy-primitives",
  "alloy-sol-types",
@@ -329,9 +329,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-network"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c1e22ff194b1e34b4defd1e257e3fe4dce0eee37451c7757a1510d6b23e7379a"
+checksum = "2b314ed5bdc7f449c53853125af2db5ac4d3954a9f4b205e7d694f02fc1932d1"
 dependencies = [
  "alloy-consensus",
  "alloy-consensus-any",
@@ -355,9 +355,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-network-primitives"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b8a6cbb9f431bdad294eebb5af9b293d6979e633bfe5468d1e87c1421a858265"
+checksum = "5e9762ac5cca67b0f6ab614f7f8314942eead1c8eeef61511ea43a6ff048dbe0"
 dependencies = [
  "alloy-consensus",
  "alloy-eips",
@@ -408,7 +408,7 @@ dependencies = [
  "cfg-if",
  "const-hex",
  "derive_more",
- "foldhash 0.2.0",
+ "foldhash",
  "getrandom 0.3.4",
  "hashbrown 0.16.1",
  "indexmap 2.12.1",
@@ -429,9 +429,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-provider"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3f5dde1abc3d582e53d139904fcdd8b2103f0bd03e8f2acb4292edbbaeaa7e6e"
+checksum = "ea8f7ca47514e7f552aa9f3f141ab17351332c6637e3bf00462d8e7c5f10f51f"
 dependencies = [
  "alloy-chains",
  "alloy-consensus",
@@ -459,7 +459,7 @@ dependencies = [
  "either",
  "futures",
  "futures-utils-wasm",
- "lru 0.13.0",
+ "lru",
  "parking_lot",
  "pin-project 1.1.10",
  "reqwest",
@@ -474,9 +474,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-pubsub"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "acbfe0a3c553a027f722185fb574124d205147fffb309cae52d0a2094f076887"
+checksum = "4082778c908aa801a1f9fdc85d758812842ab4b2aaba58e9dbe7626d708ab7e1"
 dependencies = [
  "alloy-json-rpc",
  "alloy-primitives",
@@ -518,9 +518,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-rpc-client"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5a94bdef2710322c6770be08689fee0878c2ad75615b8fc40e05d7f3c9618c0b"
+checksum = "26dd083153d2cb73cce1516f5a3f9c3af74764a2761d901581a355777468bd8f"
 dependencies = [
  "alloy-json-rpc",
  "alloy-primitives",
@@ -544,9 +544,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-rpc-types"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "811a573c8080e1b492d488e6a240ec5dd7677d7167e91ce9cb4d0ec1fcac8027"
+checksum = "8c998214325cfee1fbe61e5abaed3a435f4ca746ac7399b46feb57c364552452"
 dependencies = [
  "alloy-primitives",
  "alloy-rpc-types-anvil",
@@ -560,9 +560,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-rpc-types-anvil"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "838ca94be532a929f27961851000ec8bbbaeb06e2a2bcca44fac7855a2fe0f6f"
+checksum = "a2b03d65fcf579fbf17d3aac32271f99e2b562be04097436cd6e766b3e06613b"
 dependencies = [
  "alloy-primitives",
  "alloy-rpc-types-eth",
@@ -572,9 +572,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-rpc-types-any"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "12df0b34551ca2eab8ec83b56cb709ee5da991737282180d354a659b907f00dc"
+checksum = "4b4a6f49d161ef83354d5ba3c8bc83c8ee464cb90182b215551d5c4b846579be"
 dependencies = [
  "alloy-consensus-any",
  "alloy-rpc-types-eth",
@@ -583,9 +583,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-rpc-types-beacon"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "32598a2443750a2e884c1b48efccaeeaae75e7eb4e0f13df9146b78107b4c301"
+checksum = "3b6654644613f33fd2e6f333f4ce8ad0a26f036c0513699d7bc168bba18d412d"
 dependencies = [
  "alloy-eips",
  "alloy-primitives",
@@ -599,9 +599,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-rpc-types-debug"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6c49a3a168a5bf18f1cf7ed5723a650aebe714edf7665b53dacf5707716733d0"
+checksum = "467025b916f32645f322a085d0017f2996d0200ac89dd82a4fc2bf0f17b9afa3"
 dependencies = [
  "alloy-primitives",
  "derive_more",
@@ -611,9 +611,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-rpc-types-engine"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ffe16cd1dea6089902ec609e04261a9ae6d11ec66005ba24c1f97f0eefbc0fa9"
+checksum = "933aaaace9faa6d7efda89472add89a8bfd15270318c47a2be8bb76192c951e2"
 dependencies = [
  "alloy-consensus",
  "alloy-eips",
@@ -626,14 +626,14 @@ dependencies = [
  "jsonwebtoken",
  "rand 0.8.5",
  "serde",
- "strum 0.27.2",
+ "strum",
 ]
 
 [[package]]
 name = "alloy-rpc-types-eth"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b7f9f130511b8632686dfe6f9909b38d7ae4c68de3ce17d28991400646a39b25"
+checksum = "11920b16ab7c86052f990dcb4d25312fb2889faf506c4ee13dc946b450536989"
 dependencies = [
  "alloy-consensus",
  "alloy-consensus-any",
@@ -652,9 +652,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-rpc-types-trace"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cafe859944638c5d57d1a3a0034cdb5d07c98c37de8adce5508f28834acf958f"
+checksum = "498375e6a13b6edd04422a13d2b1a6187183e5a3aa14c5907b4c566551248bab"
 dependencies = [
  "alloy-primitives",
  "alloy-rpc-types-eth",
@@ -666,9 +666,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-rpc-types-txpool"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "afaa06544e36f223b99b1415a12911230fd527994f020736c3c7950d5080208e"
+checksum = "6d9123d321ecd70925646eb2c60b1d9b7a965f860fbd717643e2c20fcf85d48d"
 dependencies = [
  "alloy-primitives",
  "alloy-rpc-types-eth",
@@ -678,9 +678,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-serde"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "067b718d2e6ac1bb889341fcc7a250cfa49bcd3ba4f23923f1c1eb1f2b10cb7c"
+checksum = "d1a0d2d5c64881f3723232eaaf6c2d9f4f88b061c63e87194b2db785ff3aa31f"
 dependencies = [
  "alloy-primitives",
  "serde",
@@ -689,9 +689,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-signer"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "acff6b251740ef473932386d3b71657d3825daebf2217fb41a7ef676229225d4"
+checksum = "5ea4ac9765e5a7582877ca53688e041fe184880fe75f16edf0945b24a319c710"
 dependencies = [
  "alloy-dyn-abi",
  "alloy-primitives",
@@ -706,9 +706,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-signer-aws"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a4111255269e2d96b7e064ffa98f94ebc51c8e18d43501a10808c316e6d5a4d6"
+checksum = "4d4cf9b92d8e2a467942397b8b07c75bf05f32d0cbe290959a75518f18141ae8"
 dependencies = [
  "alloy-consensus",
  "alloy-network",
@@ -725,9 +725,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-signer-gcp"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b3fe5d26c2e1144aa89d65a0f1d1faec4dbf4c3ea1f7375888274c6609de2234"
+checksum = "57247cadb62bcf3eb3846cd06cc7b613583f45eb7f5062471020d260a78642b9"
 dependencies = [
  "alloy-consensus",
  "alloy-network",
@@ -743,9 +743,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-signer-ledger"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "018fe424516f3bad2aefca5ee556a9c75301d68ab5377e296f85d33d6dc446c0"
+checksum = "b2ec8823919afd43e90035113816fe8b39ff5929d4b74e4a44fedcaf53f5bbd8"
 dependencies = [
  "alloy-consensus",
  "alloy-dyn-abi",
@@ -763,9 +763,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-signer-local"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c9129ef31975d987114c27c9930ee817cf3952355834d47f2fdf4596404507e8"
+checksum = "3c9d85b9f7105ab5ce7dae7b0da33cd9d977601a48f759e1c82958978dd1a905"
 dependencies = [
  "alloy-consensus",
  "alloy-network",
@@ -783,9 +783,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-signer-trezor"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "af231a5e9b07e54cd3142ad51bd07cbb95b4ccb4db991897a0ab9e7ed052286f"
+checksum = "dbc86d2dab9480316ea953c78c105f1b4eb97356a41d75da5ed2b701105ecb35"
 dependencies = [
  "alloy-consensus",
  "alloy-network",
@@ -800,9 +800,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-signer-turnkey"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1dae31a1578b3dedbc7c07aa5376d399adcf883caca7fdd56151b7618df72634"
+checksum = "b0234aa6deab37b01e50c06845a879509fc9c5cba7ba6ec52c6ee76567cc1d58"
 dependencies = [
  "alloy-consensus",
  "alloy-network",
@@ -889,9 +889,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-transport"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bec1fb08ee484e615f24867c0b154fff5722bb00176102a16868c6532b7c3623"
+checksum = "4e72f5c4ba505ebead6a71144d72f21a70beadfb2d84e0a560a985491ecb71de"
 dependencies = [
  "alloy-json-rpc",
  "auto_impl",
@@ -912,9 +912,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-transport-http"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "64b722073c76f2de7e118d546ee1921c50710f97feb32aed50db94cfa5b663e1"
+checksum = "400dc298aaabdbd48be05448c4a19eaa38416c446043f3e54561249149269c32"
 dependencies = [
  "alloy-json-rpc",
  "alloy-transport",
@@ -927,9 +927,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-transport-ipc"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bdedcf401aab4b96d8b5e6638b79d04a6afb96c0bfcb50a2324fbadfe65c47b3"
+checksum = "ba22ff961cf99495ee4fdbaf4623f8d5483d408ca2c6e1b1a54ef438ca87f8dd"
 dependencies = [
  "alloy-json-rpc",
  "alloy-pubsub",
@@ -947,9 +947,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-transport-ws"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "942210908f0c56941097f5653a5f334546940e6fd9073495b257e52216469feb"
+checksum = "c38b4472f2bbd96a27f393de9e2f12adca0dc1075fb4d0f7c8f3557c5c600392"
 dependencies = [
  "alloy-pubsub",
  "alloy-transport",
@@ -980,9 +980,9 @@ dependencies = [
 
 [[package]]
 name = "alloy-tx-macros"
-version = "1.2.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "04950a13cc4209d8e9b78f306e87782466bad8538c94324702d061ff03e211c9"
+checksum = "e2183706e24173309b0ab0e34d3e53cf3163b71a419803b2b3b0c1fb7ff7a941"
 dependencies = [
  "darling 0.21.3",
  "proc-macro2",
@@ -2571,12 +2571,6 @@ dependencies = [
  "thiserror 1.0.69",
 ]
 
-[[package]]
-name = "cassowary"
-version = "0.3.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "df8670b8c7b9dae1793364eafadf7239c40d669904660c5960d74cfd80b46a53"
-
 [[package]]
 name = "cast"
 version = "1.5.1"
@@ -3013,7 +3007,7 @@ version = "7.2.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b03b7db8e0b4b2fdad6c551e634134e99ec000e5c8c3b6856c65e8bbaded7a3b"
 dependencies = [
- "crossterm 0.29.0",
+ "crossterm",
  "unicode-segmentation",
  "unicode-width 0.2.0",
 ]
@@ -3026,9 +3020,9 @@ checksum = "55b672471b4e9f9e95499ea597ff64941a309b2cdbffcc46f2cc5e2d971fd335"
 
 [[package]]
 name = "compact_str"
-version = "0.8.1"
+version = "0.9.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3b79c4069c6cad78e2e0cdfcbd26275770669fb39fd308a752dc110e83b9af32"
+checksum = "3fdb1325a1cece981e8a296ab8f0f9b63ae357bd0784a9faaf548cc7b480707a"
 dependencies = [
  "castaway",
  "cfg-if",
@@ -3262,22 +3256,6 @@ version = "0.8.21"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d0a5c400df2834b80a4c3327b3aad3a4c4cd4de0629063962b03235697506a28"
 
-[[package]]
-name = "crossterm"
-version = "0.28.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "829d955a0bb380ef178a640b91779e3987da38c9aea133b20614cfed8cdea9c6"
-dependencies = [
- "bitflags 2.10.0",
- "crossterm_winapi",
- "mio",
- "parking_lot",
- "rustix 0.38.44",
- "signal-hook",
- "signal-hook-mio",
- "winapi",
-]
-
 [[package]]
 name = "crossterm"
 version = "0.29.0"
@@ -3290,7 +3268,7 @@ dependencies = [
  "document-features",
  "mio",
  "parking_lot",
- "rustix 1.1.3",
+ "rustix",
  "signal-hook",
  "signal-hook-mio",
  "winapi",
@@ -3665,7 +3643,7 @@ dependencies = [
  "libc",
  "option-ext",
  "redox_users",
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -3970,7 +3948,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"
 dependencies = [
  "libc",
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -4139,7 +4117,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0ce92ff622d6dadf7349484f42c93271a0d49b7cc4d466a936405bacbe10aa78"
 dependencies = [
  "cfg-if",
- "rustix 1.1.3",
+ "rustix",
  "windows-sys 0.59.0",
 ]
 
@@ -4230,12 +4208,6 @@ version = "1.0.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3f9eec918d3f24069decb9af1554cad7c880e2da24a9afd88aca000531ab82c1"
 
-[[package]]
-name = "foldhash"
-version = "0.1.5"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d9c4f5dac5e15c24eb999c26181a6ca40b39fe946cbe4c263c7209467bc83af2"
-
 [[package]]
 name = "foldhash"
 version = "0.2.0"
@@ -4307,7 +4279,7 @@ dependencies = [
  "similar-asserts",
  "solar-compiler",
  "soldeer-commands",
- "strum 0.27.2",
+ "strum",
  "svm-rs",
  "tempfile",
  "thiserror 2.0.17",
@@ -4629,7 +4601,7 @@ dependencies = [
  "serde_json",
  "solar-compiler",
  "strsim",
- "strum 0.27.2",
+ "strum",
  "tempfile",
  "tikv-jemallocator",
  "tokio",
@@ -4863,7 +4835,7 @@ name = "foundry-debugger"
 version = "1.5.1"
 dependencies = [
  "alloy-primitives",
- "crossterm 0.29.0",
+ "crossterm",
  "eyre",
  "foundry-common",
  "foundry-compilers",
@@ -5409,8 +5381,8 @@ dependencies = [
  "libc",
  "log",
  "rustversion",
- "windows-link 0.1.3",
- "windows-result 0.3.4",
+ "windows-link 0.2.1",
+ "windows-result 0.4.1",
 ]
 
 [[package]]
@@ -5562,8 +5534,6 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9229cfe53dfd69f0609a49f65461bd93001ea1ef889cd5529dd176593f5338a1"
 dependencies = [
  "allocator-api2",
- "equivalent",
- "foldhash 0.1.5",
 ]
 
 [[package]]
@@ -5574,7 +5544,7 @@ checksum = "841d1cc9bed7f9236f321df977030373f4a4163ae1a7dbfe1a51a2c1a51d9100"
 dependencies = [
  "allocator-api2",
  "equivalent",
- "foldhash 0.2.0",
+ "foldhash",
  "serde",
  "serde_core",
 ]
@@ -5801,7 +5771,7 @@ dependencies = [
  "libc",
  "percent-encoding",
  "pin-project-lite",
- "socket2 0.5.10",
+ "socket2 0.6.1",
  "system-configuration",
  "tokio",
  "tower-service",
@@ -6178,7 +6148,7 @@ checksum = "3640c1c38b8e4e43584d8df18be5fc6b0aa314ce6ebf51b53313d4306cca8e46"
 dependencies = [
  "hermit-abi",
  "libc",
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -6336,6 +6306,17 @@ dependencies = [
  "signature",
 ]
 
+[[package]]
+name = "kasuari"
+version = "0.4.11"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "8fe90c1150662e858c7d5f945089b7517b0a80d8bf7ba4b1b5ffc984e7230a5b"
+dependencies = [
+ "hashbrown 0.16.1",
+ "portable-atomic",
+ "thiserror 2.0.17",
+]
+
 [[package]]
 name = "keccak"
 version = "0.1.5"
@@ -6472,10 +6453,13 @@ dependencies = [
 ]
 
 [[package]]
-name = "linux-raw-sys"
-version = "0.4.15"
+name = "line-clipping"
+version = "0.3.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d26c52dbd32dccf2d10cac7725f8eae5296885fb5703b261f7d0a0739ec807ab"
+checksum = "5f4de44e98ddbf09375cbf4d17714d18f39195f4f4894e8524501726fd9a8a4a"
+dependencies = [
+ "bitflags 2.10.0",
+]
 
 [[package]]
 name = "linux-raw-sys"
@@ -6528,20 +6512,11 @@ dependencies = [
 
 [[package]]
 name = "lru"
-version = "0.12.5"
+version = "0.16.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "234cf4f4a04dc1f57e24b96cc0cd600cf2af460d4161ac5ecdd0af8e1f3b2a38"
+checksum = "a1dc47f592c06f33f8e3aea9591776ec7c9f9e4124778ff8a3c3b87159f7e593"
 dependencies = [
- "hashbrown 0.15.5",
-]
-
-[[package]]
-name = "lru"
-version = "0.13.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "227748d55f2f0ab4735d87fd623798cb6b664512fe979705f829c9f81c934465"
-dependencies = [
- "hashbrown 0.15.5",
+ "hashbrown 0.16.1",
 ]
 
 [[package]]
@@ -6924,7 +6899,7 @@ version = "0.50.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7957b9740744892f114936ab4a57b3f487491bbeafaf8083688b16841a4240e5"
 dependencies = [
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -7986,9 +7961,9 @@ dependencies = [
 
 [[package]]
 name = "protobuf"
-version = "3.3.0"
+version = "3.7.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b65f4a8ec18723a734e5dc09c173e0abf9690432da5340285d536edcb4dac190"
+checksum = "d65a1d4ddae7d8b5de68153b48f6aa3bba8cb002b243dbdbc55a5afbc98f99f4"
 dependencies = [
  "once_cell",
  "protobuf-support",
@@ -7997,9 +7972,9 @@ dependencies = [
 
 [[package]]
 name = "protobuf-support"
-version = "3.3.0"
+version = "3.7.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6872f4d4f4b98303239a2b5838f5bbbb77b01ffc892d627957f37a22d7cfe69c"
+checksum = "3e36c2f31e0a47f9280fb347ef5e461ffcd2c52dd520d8e216b52f93b0b0d7d6"
 dependencies = [
  "thiserror 1.0.69",
 ]
@@ -8074,7 +8049,7 @@ dependencies = [
  "quinn-udp",
  "rustc-hash",
  "rustls",
- "socket2 0.5.10",
+ "socket2 0.6.1",
  "thiserror 2.0.17",
  "tokio",
  "tracing",
@@ -8111,9 +8086,9 @@ dependencies = [
  "cfg_aliases",
  "libc",
  "once_cell",
- "socket2 0.5.10",
+ "socket2 0.6.1",
  "tracing",
- "windows-sys 0.59.0",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
@@ -8230,25 +8205,67 @@ dependencies = [
 
 [[package]]
 name = "ratatui"
-version = "0.29.0"
+version = "0.30.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "eabd94c2f37801c20583fc49dd5cd6b0ba68c716787c2dd6ed18571e1e63117b"
+checksum = "d1ce67fb8ba4446454d1c8dbaeda0557ff5e94d39d5e5ed7f10a65eb4c8266bc"
+dependencies = [
+ "instability",
+ "ratatui-core",
+ "ratatui-crossterm",
+ "ratatui-widgets",
+]
+
+[[package]]
+name = "ratatui-core"
+version = "0.1.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "5ef8dea09a92caaf73bff7adb70b76162e5937524058a7e5bff37869cbbec293"
 dependencies = [
  "bitflags 2.10.0",
- "cassowary",
  "compact_str",
- "crossterm 0.28.1",
+ "hashbrown 0.16.1",
  "indoc",
- "instability",
- "itertools 0.13.0",
- "lru 0.12.5",
- "paste",
- "strum 0.26.3",
+ "itertools 0.14.0",
+ "kasuari",
+ "lru",
+ "strum",
+ "thiserror 2.0.17",
  "unicode-segmentation",
  "unicode-truncate",
  "unicode-width 0.2.0",
 ]
 
+[[package]]
+name = "ratatui-crossterm"
+version = "0.1.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "577c9b9f652b4c121fb25c6a391dd06406d3b092ba68827e6d2f09550edc54b3"
+dependencies = [
+ "cfg-if",
+ "crossterm",
+ "instability",
+ "ratatui-core",
+]
+
+[[package]]
+name = "ratatui-widgets"
+version = "0.3.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d7dbfa023cd4e604c2553483820c5fe8aa9d71a42eea5aa77c6e7f35756612db"
+dependencies = [
+ "bitflags 2.10.0",
+ "hashbrown 0.16.1",
+ "indoc",
+ "instability",
+ "itertools 0.14.0",
+ "line-clipping",
+ "ratatui-core",
+ "strum",
+ "time",
+ "unicode-segmentation",
+ "unicode-width 0.2.0",
+]
+
 [[package]]
 name = "rayon"
 version = "1.11.0"
@@ -8897,19 +8914,6 @@ dependencies = [
  "tracing",
 ]
 
-[[package]]
-name = "rustix"
-version = "0.38.44"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fdb5bc1ae2baa591800df16c9ca78619bf65c0488b41b96ccec5d11220d8c154"
-dependencies = [
- "bitflags 2.10.0",
- "errno",
- "libc",
- "linux-raw-sys 0.4.15",
- "windows-sys 0.59.0",
-]
-
 [[package]]
 name = "rustix"
 version = "1.1.3"
@@ -8919,8 +8923,8 @@ dependencies = [
  "bitflags 2.10.0",
  "errno",
  "libc",
- "linux-raw-sys 0.11.0",
- "windows-sys 0.59.0",
+ "linux-raw-sys",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -9652,7 +9656,7 @@ dependencies = [
  "solar-data-structures",
  "solar-interface",
  "solar-macros",
- "strum 0.27.2",
+ "strum",
 ]
 
 [[package]]
@@ -9676,7 +9680,7 @@ version = "0.1.8"
 source = "git+https://github.com/paradigmxyz/solar.git?rev=1f28069#1f2806951b5c6a166edd975ebd797a3ebd5ff9f1"
 dependencies = [
  "colorchoice",
- "strum 0.27.2",
+ "strum",
 ]
 
 [[package]]
@@ -9716,7 +9720,7 @@ dependencies = [
  "solar-config",
  "solar-data-structures",
  "solar-macros",
- "thiserror 1.0.69",
+ "thiserror 2.0.17",
  "tracing",
  "unicode-width 0.2.0",
 ]
@@ -9773,7 +9777,7 @@ dependencies = [
  "solar-interface",
  "solar-macros",
  "solar-parse",
- "strum 0.27.2",
+ "strum",
  "thread_local",
  "tracing",
 ]
@@ -9913,35 +9917,13 @@ version = "0.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7da8b5736845d9f2fcb837ea5d9e2628564b3b043a70948a3f0b778838c5fb4f"
 
-[[package]]
-name = "strum"
-version = "0.26.3"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8fec0f0aef304996cf250b31b5a10dee7980c85da9d759361292b8bca5a18f06"
-dependencies = [
- "strum_macros 0.26.4",
-]
-
 [[package]]
 name = "strum"
 version = "0.27.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "af23d6f6c1a224baef9d3f61e287d2761385a5b88fdab4eb4c6f11aeb54c4bcf"
 dependencies = [
- "strum_macros 0.27.2",
-]
-
-[[package]]
-name = "strum_macros"
-version = "0.26.4"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4c6bee85a5a24955dc440386795aa378cd9cf82acd5f764469152d2270e581be"
-dependencies = [
- "heck",
- "proc-macro2",
- "quote",
- "rustversion",
- "syn 2.0.113",
+ "strum_macros",
 ]
 
 [[package]]
@@ -10042,9 +10024,9 @@ dependencies = [
 
 [[package]]
 name = "svm-rs"
-version = "0.5.23"
+version = "0.5.22"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "415b159b54c22d9810087f0991371fd6242a912673e982a7c4ca8ea122f7e00a"
+checksum = "909e8ff825120cd2b34ceb236ab72e2a7f74b1d3a86c247936c8ff7a80c5d408"
 dependencies = [
  "const-hex",
  "dirs",
@@ -10054,7 +10036,7 @@ dependencies = [
  "serde_json",
  "sha2",
  "tempfile",
- "thiserror 1.0.69",
+ "thiserror 2.0.17",
  "url",
  "zip",
 ]
@@ -10167,8 +10149,8 @@ dependencies = [
  "fastrand",
  "getrandom 0.3.4",
  "once_cell",
- "rustix 1.1.3",
- "windows-sys 0.59.0",
+ "rustix",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -10208,7 +10190,7 @@ version = "1.2.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d8c27177b12a6399ffc08b98f76f7c9a1f4fe9fc967c784c5a071fa8d93cf7e1"
 dependencies = [
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -10217,7 +10199,7 @@ version = "0.4.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "60b8cb979cb11c32ce1603f8137b22262a9d131aaa5c37b5678025f22b8becd0"
 dependencies = [
- "rustix 1.1.3",
+ "rustix",
  "windows-sys 0.60.2",
 ]
 
@@ -10836,15 +10818,15 @@ dependencies = [
 
 [[package]]
 name = "trezor-client"
-version = "0.1.4"
+version = "0.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "10636211ab89c96ed2824adc5ec0d081e1080aeacc24c37abb318dcb31dcc779"
+checksum = "87873db279766278a7e56b01139943e00a45afc079fc8fa6651e949f2234c3f6"
 dependencies = [
  "byteorder",
  "hex",
  "protobuf",
  "rusb",
- "thiserror 1.0.69",
+ "thiserror 2.0.17",
  "tracing",
 ]
 
@@ -11042,13 +11024,13 @@ checksum = "f6ccf251212114b54433ec949fd6a7841275f9ada20dddd2f29e9ceea4501493"
 
 [[package]]
 name = "unicode-truncate"
-version = "1.1.0"
+version = "2.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b3644627a5af5fa321c95b9b235a72fd24cd29c648c2c379431e6628655627bf"
+checksum = "8fbf03860ff438702f3910ca5f28f8dac63c1c11e7efb5012b8b175493606330"
 dependencies = [
  "itertools 0.13.0",
  "unicode-segmentation",
- "unicode-width 0.1.14",
+ "unicode-width 0.2.0",
 ]
 
 [[package]]
@@ -11488,7 +11470,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d3fabb953106c3c8eea8306e4393700d7657561cb43122571b172bbfb7c7ba1d"
 dependencies = [
  "env_home",
- "rustix 1.1.3",
+ "rustix",
  "winsafe",
 ]
 
@@ -11520,7 +11502,7 @@ version = "0.1.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c2a7b1c03c876122aa43f3020e6c3c3ee5c05081c9a00739faf7503aeba10d22"
 dependencies = [
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
```

### Cargo.toml
```diff
@@ -242,47 +242,47 @@ svm = { package = "svm-rs", version = "0.5", default-features = false, features
 ] }
 
 ## alloy
-alloy-consensus = { version = "1.2.1", default-features = false }
-alloy-contract = { version = "1.2.1", default-features = false }
-alloy-eips = { version = "1.2.1", default-features = false }
-alloy-eip5792 = { version = "1.2.1", default-features = false }
-alloy-ens = { version = "1.2.1", default-features = false }
-alloy-genesis = { version = "1.2.1", default-features = false }
-alloy-json-rpc = { version = "1.2.1", default-features = false }
-alloy-network = { version = "1.2.1", default-features = false }
-alloy-provider = { version = "1.2.1", default-features = false }
-alloy-pubsub = { version = "1.2.1", default-features = false }
-alloy-rpc-client = { version = "1.2.1", default-features = false }
-alloy-rpc-types = { version = "1.2.1", default-features = true }
-alloy-rpc-types-beacon = { version = "1.2.1", default-features = true }
-alloy-rpc-types-eth = { version = "1.2.1", default-features = false }
-alloy-serde = { version = "1.2.1", default-features = false }
-alloy-signer = { version = "1.2.1", default-features = false }
-alloy-signer-aws = { version = "1.2.1", default-features = false }
-alloy-signer-gcp = { version = "1.2.1", default-features = false }
-alloy-signer-ledger = { version = "1.2.1", default-features = false }
-alloy-signer-local = { version = "1.2.1", default-features = false }
-alloy-signer-trezor = { version = "1.2.1", default-features = false }
-alloy-signer-turnkey = { version = "1.2.1", default-features = false }
-alloy-transport = { version = "1.2.1", default-features = false }
-alloy-transport-http = { version = "1.2.1", default-features = false }
-alloy-transport-ipc = { version = "1.2.1", default-features = false }
-alloy-transport-ws = { version = "1.2.1", default-features = false }
+alloy-consensus = { version = "1.4", default-features = false }
+alloy-contract = { version = "1.4", default-features = false }
+alloy-eips = { version = "1.4", default-features = false }
+alloy-eip5792 = { version = "1.4", default-features = false }
+alloy-ens = { version = "1.4", default-features = false }
+alloy-genesis = { version = "1.4", default-features = false }
+alloy-json-rpc = { version = "1.4", default-features = false }
+alloy-network = { version = "1.4", default-features = false }
+alloy-provider = { version = "1.4", default-features = false }
+alloy-pubsub = { version = "1.4", default-features = false }
+alloy-rpc-client = { version = "1.4", default-features = false }
+alloy-rpc-types = { version = "1.4", default-features = true }
+alloy-rpc-types-beacon = { version = "1.4", default-features = true }
+alloy-rpc-types-eth = { version = "1.4", default-features = false }
+alloy-serde = { version = "1.4", default-features = false }
+alloy-signer = { version = "1.4", default-features = false }
+alloy-signer-aws = { version = "1.4", default-features = false }
+alloy-signer-gcp = { version = "1.4", default-features = false }
+alloy-signer-ledger = { version = "1.4", default-features = false }
+alloy-signer-local = { version = "1.4", default-features = false }
+alloy-signer-trezor = { version = "1.4", default-features = false }
+alloy-signer-turnkey = { version = "1.4", default-features = false }
+alloy-transport = { version = "1.4", default-features = false }
+alloy-transport-http = { version = "1.4", default-features = false }
+alloy-transport-ipc = { version = "1.4", default-features = false }
+alloy-transport-ws = { version = "1.4", default-features = false }
 alloy-hardforks = { version = "0.4.7", default-features = false }
 alloy-op-hardforks = { version = "0.4.7", default-features = false }
 
 ## alloy-core
-alloy-dyn-abi = "1.5.1"
-alloy-json-abi = "1.5.1"
-alloy-primitives = { version = "1.5.1", features = [
+alloy-dyn-abi = "1.5.2"
+alloy-json-abi = "1.5.2"
+alloy-primitives = { version = "1.5.2", features = [
     "getrandom",
     "rand",
     "map-fxhash",
     "map-foldhash",
 ] }
-alloy-sol-macro-expander = "1.5.1"
-alloy-sol-macro-input = "1.5.1"
-alloy-sol-types = "1.5.1"
+alloy-sol-macro-expander = "1.5.2"
+alloy-sol-macro-input = "1.5.2"
+alloy-sol-types = "1.5.2"
 
 alloy-chains = "0.2"
 alloy-rlp = "0.3"
```

### crates/anvil/src/eth/backend/mem/mod.rs
```diff
@@ -3267,7 +3267,7 @@ impl Backend {
             && let Ok(typed_tx) = FoundryTxEnvelope::try_from(tx)
             && let Some(sidecar) = typed_tx.sidecar()
         {
-            return Ok(Some(sidecar.sidecar.blobs.clone()));
+            return Ok(Some(sidecar.sidecar.blobs().to_vec()));
         }
 
         Ok(None)
@@ -3285,7 +3285,7 @@ impl Backend {
                 .iter()
                 .filter_map(|tx| tx.as_ref().sidecar())
                 .flat_map(|sidecar| {
-                    sidecar.sidecar.blobs.iter().zip(sidecar.sidecar.commitments.iter())
+                    sidecar.sidecar.blobs().iter().zip(sidecar.sidecar.commitments().iter())
                 })
                 .filter(|(_, commitment)| {
                     // Filter blobs by versioned_hashes if provided
@@ -3306,10 +3306,10 @@ impl Backend {
                     for versioned_hash in sidecar.sidecar.versioned_hashes() {
                         if versioned_hash == hash
                             && let Some(index) =
-                                sidecar.sidecar.commitments.iter().position(|commitment| {
+                                sidecar.sidecar.commitments().iter().position(|commitment| {
                                     kzg_to_versioned_hash(commitment.as_slice()) == *hash
                                 })
-                            && let Some(blob) = sidecar.sidecar.blobs.get(index)
+                            && let Some(blob) = sidecar.sidecar.blobs().get(index)
                         {
                             return Ok(Some(*blob));
                         }
```

### crates/anvil/tests/it/api.rs
```diff
@@ -4,7 +4,10 @@ use crate::{
     abi::{Multicall, SimpleStorage, VendingMachine},
     utils::{connect_pubsub_with_wallet, http_provider, http_provider_with_signer},
 };
-use alloy_consensus::{SidecarBuilder, SignableTransaction, SimpleCoder, Transaction, TxEip1559};
+use alloy_consensus::{
+    BlobTransactionSidecar, SidecarBuilder, SignableTransaction, SimpleCoder, Transaction,
+    TxEip1559,
+};
 use alloy_network::{
     EthereumWallet, ReceiptResponse, TransactionBuilder, TransactionBuilder4844, TxSignerSync,
 };
@@ -567,7 +570,7 @@ async fn test_fill_transaction_eip4844_blob_fee() {
 
     let mut builder = SidecarBuilder::<SimpleCoder>::new();
     builder.ingest(b"dummy blob");
-    let sidecar = builder.build().unwrap();
+    let sidecar: BlobTransactionSidecar = builder.build().unwrap();
 
     // EIP-4844 blob transaction with sidecar but no blob fee
     let mut tx_req = TransactionRequest::default().with_from(from).with_to(Address::random());
@@ -595,7 +598,7 @@ async fn test_fill_transaction_eip4844_preserves_blob_fee() {
 
     let mut builder = SidecarBuilder::<SimpleCoder>::new();
     builder.ingest(b"dummy blob");
-    let sidecar = builder.build().unwrap();
+    let sidecar: BlobTransactionSidecar = builder.build().unwrap();
 
     // EIP-4844 blob transaction with blob fee already set
     let mut tx_req = TransactionRequest::default()
```

### crates/anvil/tests/it/eip4844.rs
```diff
@@ -1,5 +1,5 @@
 use crate::utils::{http_provider, http_provider_with_signer};
-use alloy_consensus::{SidecarBuilder, SimpleCoder, Transaction};
+use alloy_consensus::{BlobTransactionSidecar, SidecarBuilder, SimpleCoder, Transaction};
 use alloy_eips::{
     Typed2718,
     eip4844::{BLOB_TX_MIN_BLOB_GASPRICE, DATA_GAS_PER_BLOB, MAX_DATA_GAS_PER_BLOCK_DENCUN},
@@ -62,7 +62,7 @@ async fn can_send_eip4844_transaction_fork() {
     let bob = accounts[1];
 
     let sidecar: SidecarBuilder<SimpleCoder> = SidecarBuilder::from_slice(b"Blobs are fun!");
-    let sidecar = sidecar.build().unwrap();
+    let sidecar: BlobTransactionSidecar = sidecar.build().unwrap();
 
     let tx = TransactionRequest::default()
         .with_from(alice)
@@ -89,7 +89,7 @@ async fn can_send_eip4844_transaction_eth_send_transaction() {
     let bob = accounts[1];
 
     let sidecar: SidecarBuilder<SimpleCoder> = SidecarBuilder::from_slice(b"Blobs are fun!");
-    let sidecar = sidecar.build().unwrap();
+    let sidecar: BlobTransactionSidecar = sidecar.build().unwrap();
 
     let tx = TransactionRequest::default()
         .with_from(alice)
@@ -417,7 +417,7 @@ async fn can_get_blobs_by_versioned_hash() {
 
     let sidecar: SidecarBuilder<SimpleCoder> = SidecarBuilder::from_slice(b"Hello World");
 
-    let sidecar = sidecar.build().unwrap();
+    let sidecar: BlobTransactionSidecar = sidecar.build().unwrap();
     let tx = TransactionRequest::default()
         .with_from(from)
         .with_to(to)
@@ -455,7 +455,7 @@ async fn can_get_blobs_by_tx_hash() {
 
     let sidecar: SidecarBuilder<SimpleCoder> = SidecarBuilder::from_slice(b"Hello World");
 
-    let sidecar = sidecar.build().unwrap();
+    let sidecar: BlobTransactionSidecar = sidecar.build().unwrap();
     let tx = TransactionRequest::default()
         .with_from(from)
         .with_to(to)
```

### crates/debugger/Cargo.toml
```diff
@@ -23,7 +23,7 @@ alloy-primitives.workspace = true
 
 crossterm = "0.29"
 eyre.workspace = true
-ratatui = { version = "0.29", default-features = false, features = [
+ratatui = { version = "0.30", default-features = false, features = [
     "crossterm",
 ] }
 revm.workspace = true
```

### deny.toml
```diff
@@ -7,12 +7,6 @@ yanked = "warn"
 ignore = [
     # https://rustsec.org/advisories/RUSTSEC-2024-0436 paste! is unmaintained
     "RUSTSEC-2024-0436",
-    # https://rustsec.org/advisories/RUSTSEC-2024-0437 protobuf! Crash due to uncontrolled recursion in protobuf crate.
-    "RUSTSEC-2024-0437",
-    # https://rustsec.org/advisories/RUSTSEC-2025-0141 bincode is unmaintained, need to transition all deps to wincode first
-    "RUSTSEC-2025-0141",
-    #  https://rustsec.org/advisories/RUSTSEC-2026-0002 lru unused directly: <https://github.com/alloy-rs/alloy/pull/3460>
-    "RUSTSEC-2026-0002",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
