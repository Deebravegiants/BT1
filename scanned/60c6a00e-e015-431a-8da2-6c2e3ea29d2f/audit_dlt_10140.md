# [?] fix: RUSTSEC-2021-0145 replace atty with is-terminal

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2023-04-11
Source: https://github.com/nervosnetwork/ckb/commit/88593c5121b444464fbfeea2ad91c34f31c652b5
Type: security-commit

## Details
fix: RUSTSEC-2021-0145 replace atty with is-terminal

## Patch
### Cargo.lock
```diff
@@ -151,7 +151,7 @@ version = "0.63.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "36d860121800b2a9a94f9b5604b332d5cffb234ce17609ea479d723dbc9d3885"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
  "cexpr",
  "clang-sys",
  "lazy_static",
@@ -188,12 +188,6 @@ version = "1.3.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bef38d45163c2f1dde094a7dfd33ccf595c92905c8f8f4fdc18d06fb1037718a"
 
-[[package]]
-name = "bitflags"
-version = "2.0.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "487f1e0fcbe47deb8b0574e646def1c903389d95241dd1bbcc6ce4a715dfc0c1"
-
 [[package]]
 name = "blake2b-ref"
 version = "0.2.1"
@@ -422,7 +416,7 @@ dependencies = [
  "ckb-resource",
  "ckb-systemtime",
  "ckb-types",
- "clap 4.1.11",
+ "clap 4.1.14",
  "path-clean",
  "rand 0.7.3",
  "sentry",
@@ -479,7 +473,6 @@ dependencies = [
 name = "ckb-bin"
 version = "0.109.0-rc1"
 dependencies = [
- "atty",
  "base64",
  "ckb-app-config",
  "ckb-async-runtime",
@@ -504,9 +497,10 @@ dependencies = [
  "ckb-types",
  "ckb-util",
  "ckb-verification-traits",
- "clap 4.1.11",
+ "clap 4.1.14",
  "ctrlc",
  "fdlimit",
+ "is-terminal",
  "rayon",
  "sentry",
  "serde",
@@ -998,7 +992,7 @@ dependencies = [
 name = "ckb-network"
 version = "0.109.0-rc1"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
  "bloom-filters",
  "bs58",
  "ckb-app-config",
@@ -1320,7 +1314,7 @@ dependencies = [
 name = "ckb-sync"
 version = "0.109.0-rc1"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
  "ckb-app-config",
  "ckb-async-runtime",
  "ckb-chain",
@@ -1519,7 +1513,7 @@ dependencies = [
 name = "ckb-verification-traits"
 version = "0.109.0-rc1"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
  "ckb-error",
 ]
 
@@ -1560,24 +1554,33 @@ dependencies = [
 
 [[package]]
 name = "clap"
-version = "3.2.21"
+version = "3.2.23"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1ed5341b2301a26ab80be5cbdced622e80ed808483c52e45e3310a877d3b37d7"
+checksum = "71655c45cb9845d3270c9d6df84ebe72b4dad3c2ba3f7023ad47c144e4e473a5"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
  "clap_lex 0.2.3",
  "indexmap",
  "textwrap",
 ]
 
 [[package]]
 name = "clap"
-version = "4.1.11"
+version = "4.1.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "42dfd32784433290c51d92c438bb72ea5063797fc3cc9a21a8c4346bebbb2098"
+checksum = "906f7fe1da4185b7a282b2bc90172a496f9def1aca4545fe7526810741591e14"
 dependencies = [
- "bitflags 2.0.2",
- "clap_lex 0.3.0",
+ "clap_builder",
+]
+
+[[package]]
+name = "clap_builder"
+version = "4.1.14"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "351f9ad9688141ed83dfd8f5fb998a06225ef444b48ff4dc43de6d409b7fd10b"
+dependencies = [
+ "bitflags",
+ "clap_lex 0.4.1",
  "is-terminal",
  "strsim",
  "termcolor",
@@ -1594,12 +1597,9 @@ dependencies = [
 
 [[package]]
 name = "clap_lex"
-version = "0.3.0"
+version = "0.4.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0d4198f73e42b4936b35b5bb248d81d2b595ecb170da0bac7655c54eedfa8da8"
-dependencies = [
- "os_str_bytes",
-]
+checksum = "8a2dd5a6fe8c6e3502f568a6353e5273bbb15193ad9a89e457b9970798efbea1"
 
 [[package]]
 name = "console"
@@ -1686,7 +1686,7 @@ dependencies = [
  "atty",
  "cast",
  "ciborium",
- "clap 3.2.21",
+ "clap 3.2.23",
  "criterion-plot",
  "itertools",
  "lazy_static",
@@ -1990,6 +1990,17 @@ dependencies = [
  "winapi 0.3.9",
 ]
 
+[[package]]
+name = "errno"
+version = "0.3.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4bcfec3a70f97c962c307b2d2c56e358cf1d00b558d74262b5f929ee8cc7e73a"
+dependencies = [
+ "errno-dragonfly",
+ "libc",
+ "windows-sys 0.48.0",
+]
+
 [[package]]
 name = "errno-dragonfly"
 version = "0.1.2"
@@ -2133,7 +2144,7 @@ version = "0.3.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2e9763c69ebaae630ba35f74888db465e49e259ba1bc0eda7d06f4a067615d82"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
  "fuchsia-zircon-sys",
 ]
 
@@ -2441,6 +2452,12 @@ dependencies = [
  "libc",
 ]
 
+[[package]]
+name = "hermit-abi"
+version = "0.3.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "fed44880c466736ef9a5c5b5facefb5ed0785676d0c02d612db14e54f0d84286"
+
 [[package]]
 name = "hex"
 version = "0.4.3"
@@ -2686,14 +2703,14 @@ dependencies = [
 
 [[package]]
 name = "is-terminal"
-version = "0.4.2"
+version = "0.4.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "28dfb6c8100ccc63462345b67d1bbc3679177c75ee4bf59bf29c8b1d110b8189"
+checksum = "adcf93614601c8129ddf72e2d5633df827ba6551541c6d8c59520a371475be1f"
 dependencies = [
- "hermit-abi 0.2.6",
+ "hermit-abi 0.3.1",
  "io-lifetimes",
- "rustix",
- "windows-sys 0.42.0",
+ "rustix 0.37.7",
+ "windows-sys 0.48.0",
 ]
 
 [[package]]
@@ -2907,6 +2924,12 @@ version = "0.1.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f051f77a7c8e6957c0696eac88f26b0117e54f52d3fc682ab19397a8812846a4"
 
+[[package]]
+name = "linux-raw-sys"
+version = "0.3.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d59d8c75012853d2e872fb56bc8a2e53718e2cafe1a4c823143141c6d90c322f"
+
 [[package]]
 name = "lock_api"
 version = "0.4.6"
@@ -3110,7 +3133,7 @@ version = "0.23.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9f866317acbd3a240710c63f065ffb1e4fd466259045ccb504130b7f668f35c6"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
  "cc",
  "cfg-if 1.0.0",
  "libc",
@@ -3260,7 +3283,7 @@ version = "0.10.48"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "518915b97df115dd36109bfa429a48b8f737bd05508cf9588977b599648926d2"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
  "cfg-if 1.0.0",
  "foreign-types",
  "libc",
@@ -3604,7 +3627,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "29f1b898011ce9595050a68e60f90bad083ff2987a695a42357134c8381fba70"
 dependencies = [
  "bit-set",
- "bitflags 1.3.2",
+ "bitflags",
  "byteorder",
  "lazy_static",
  "num-traits",
@@ -3783,7 +3806,7 @@ version = "0.2.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8383f39639269cde97d255a32bdb68c047337295414940c68bdd30c2e13203ff"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
 ]
 
 [[package]]
@@ -3857,7 +3880,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4ff176e72a35d975ea0759b1bed69e30ad5cf47580b2e5d00449e8623b5a37dc"
 dependencies = [
  "ahash 0.8.2",
- "bitflags 1.3.2",
+ "bitflags",
  "instant",
  "num-traits",
  "rhai_codegen",
@@ -3928,14 +3951,28 @@ version = "0.36.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4feacf7db682c6c329c4ede12649cd36ecab0f3be5b7d74e6a20304725db4549"
 dependencies = [
- "bitflags 1.3.2",
- "errno",
+ "bitflags",
+ "errno 0.2.8",
  "io-lifetimes",
  "libc",
- "linux-raw-sys",
+ "linux-raw-sys 0.1.4",
  "windows-sys 0.42.0",
 ]
 
+[[package]]
+name = "rustix"
+version = "0.37.7"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "2aae838e49b3d63e9274e1c01833cc8139d3fec468c3b84688c628f44b1ae11d"
+dependencies = [
+ "bitflags",
+ "errno 0.3.1",
+ "io-lifetimes",
+ "libc",
+ "linux-raw-sys 0.3.1",
+ "windows-sys 0.45.0",
+]
+
 [[package]]
 name = "rusty-fork"
 version = "0.3.0"
@@ -4023,7 +4060,7 @@ version = "2.6.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2dc14f172faf8a0194a3aded622712b0de276821addc574fa54fc0a1167e10dc"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags",
  "core-foundation",
  "core-foundation-sys",
  "libc",
@@ -4355,7 +4392,7 @@ dependencies = [
  "cfg-if 1.0.0",
  "fastrand",
  "redox_syscall",
- "rustix",
+ "rustix 0.36.6",
  "windows-sys 0.42.0",
 ]
 
@@ -4440,9 +4477,9 @@ dependencies = [
 
 [[package]]
 name = "textwrap"
-version = "0.15.0"
+version = "0.16.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b1141d4d61095b28419e22cb0bbf02755f5e54e0526f97f1e3d1d160e60885fb"
+checksum = "222a222a5bfe1bba4a77b45ec488a741b3cb8872e5e499451fd7d0129c9c7c3d"
 
 [[package]]
 name = "thiserror"
@@ -5087,20 +5124,74 @@ version = "0.42.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5a3e1820f08b8513f676f7ab6c1f99ff312fb97b553d30ff4dd86f9f15728aa7"
 dependencies = [
- "windows_aarch64_gnullvm",
- "windows_aarch64_msvc 0.42.0",
- "windows_i686_gnu 0.42.0",
- "windows_i686_msvc 0.42.0",
- "windows_x86_64_gnu 0.42.0",
- "windows_x86_64_gnullvm",
- "windows_x86_64_msvc 0.42.0",
+ "windows_aarch64_gnullvm 0.42.2",
+ "windows_aarch64_msvc 0.42.2",
+ "windows_i686_gnu 0.42.2",
+ "windows_i686_msvc 0.42.2",
+ "windows_x86_64_gnu 0.42.2",
+ "windows_x86_64_gnullvm 0.42.2",
+ "windows_x86_64_msvc 0.42.2",
+]
+
+[[package]]
+name = "windows-sys"
+version = "0.45.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "75283be5efb2831d37ea142365f009c02ec203cd29a3ebecbc093d52315b66d0"
+dependencies = [
+ "windows-targets 0.42.2",
+]
+
+[[package]]
+name = "windows-sys"
+version = "0.48.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "677d2418bec65e3338edb076e806bc1ec15693c5d0104683f2efe857f61056a9"
+dependencies = [
+ "windows-targets 0.48.0",
+]
+
+[[package]]
+name = "windows-targets"
+version = "0.42.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "8e5180c00cd44c9b1c88adb3693291f1cd93605ded80c250a75d472756b4d071"
+dependencies = [
+ "windows_aarch64_gnullvm 0.42.2",
+ "windows_aarch64_msvc 0.42.2",
+ "windows_i686_gnu 0.42.2",
+ "windows_i686_msvc 0.42.2",
+ "windows_x86_64_gnu 0.42.2",
+ "windows_x86_64_gnullvm 0.42.2",
+ "windows_x86_64_msvc 0.42.2",
+]
+
+[[package]]
+name = "windows-targets"
+version = "0.48.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7b1eb6f0cd7c80c79759c929114ef071b87354ce476d9d94271031c0497adfd5"
+dependencies = [
+ "windows_aarch64_gnullvm 0.48.0",
+ "windows_aarch64_msvc 0.48.0",
+ "windows_i686_gnu 0.48.0",
+ "windows_i686_msvc 0.48.0",
+ "windows_x86_64_gnu 0.48.0",
+ "windows_x86_64_gnullvm 0.48.0",
+ "windows_x86_64_msvc 0.48.0",
 ]
 
 [[package]]
 name = "windows_aarch64_gnullvm"
-version = "0.42.0"
+version = "0.42.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "41d2aa71f6f0cbe00ae5167d90ef3cfe66527d6f613ca78ac8024c3ccab9a19e"
+checksum = "597a5118570b68bc08d8d59125332c54f1ba9d9adeedeef5b99b02ba2b0698f8"
+
+[[package]]
+name = "windows_aarch64_gnullvm"
+version = "0.48.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "91ae572e1b79dba883e0d315474df7305d12f569b400fcf90581b06062f7e1bc"
 
 [[package]]
 name = "windows_aarch64_msvc"
@@ -5110,9 +5201,15 @@ checksum = "9bb8c3fd39ade2d67e9874ac4f3db21f0d710bee00fe7cab16949ec184eeaa47"
 
 [[package]]
 name = "windows_aarch64_msvc"
-version = "0.42.0"
+version = "0.42.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e08e8864a60f06ef0d0ff4ba04124db8b0fb3be5776a5cd47641e942e58c4d43"
+
+[[package]]
+name = "windows_aarch64_msvc"
+version = "0.48.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dd0f252f5a35cac83d6311b2e795981f5ee6e67eb1f9a7f64eb4500fbc4dcdb4"
+checksum = "b2ef27e0d7bdfcfc7b868b317c1d32c641a6fe4629c171b8928c7b08d98d7cf3"
 
 [[package]]
 name = "windows_i686_gnu"
@@ -5122,9 +5219,15 @@ checksum = "180e6ccf01daf4c426b846dfc66db1fc518f074baa793aa7d9b9aaeffad6a3b6"
 
 [[package]]
 name = "windows_i686_gnu"
-version = "0.42.0"
+version = "0.42.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fbeae19f6716841636c28d695375df17562ca208b2b7d0dc47635a50ae6c5de7"
+checksum = "c61d927d8da41da96a81f029489353e68739737d3beca43145c8afec9a31a84f"
+
+[[package]]
+name = "windows_i686_gnu"
+version = "0.48.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "622a1962a7db830d6fd0a69683c80a18fda201879f0f447f065a3b7467daa241"
 
 [[package]]
 name = "windows_i686_msvc"
@@ -5134,9 +5237,15 @@ checksum = "e2e7917148b2812d1eeafaeb22a97e4813dfa60a3f8f78ebe204bcc88f12f024"
 
 [[package]]
 name = "windows_i686_msvc"
-version = "0.42.0"
+version = "0.42.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "84c12f65daa39dd2babe6e442988fc329d6243fdce47d7d2d155b8d874862246"
+checksum = "44d840b6ec649f480a41c8d80f9c65108b92d89345dd94027bfe06ac444d1060"
+
+[[package]]
+name = "windows_i686_msvc"
+version = "0.48.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4542c6e364ce21bf45d69fdd2a8e455fa38d316158cfd43b3ac1c5b1b19f8e00"
 
 [[package]]
 name = "windows_x86_64_gnu"
@@ -5146,15 +5255,27 @@ checksum = "4dcd171b8776c41b97521e5da127a2d86ad280114807d0b2ab1e462bc764d9e1"
 
 [[package]]
 name = "windows_x86_64_gnu"
-version = "0.42.0"
+version = "0.42.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "8de912b8b8feb55c064867cf047dda097f92d51efad5b491dfb98f6bbb70cb36"
+
+[[package]]
+name = "windows_x86_64_gnu"
+version = "0.48.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bf7b1b21b5362cbc318f686150e5bcea75ecedc74dd157d874d754a2ca44b0ed"
+checksum = "ca2b8a661f7628cbd23440e50b05d705db3686f894fc9580820623656af974b1"
 
 [[package]]
 name = "windows_x86_64_gnullvm"
-version = "0.42.0"
+version = "0.42.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "09d525d2ba30eeb3297665bd434a54297e4170c7f1a44cad4ef58095b4cd2028"
+checksum = "26d41b46a36d453748aedef1486d5c7a85db22e56aff34643984ea85514e94a3"
+
+[[package]]
+name = "windows_x86_64_gnullvm"
+version = "0.48.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7896dbc1f41e08872e9d5e8f8baa8fdd2677f29468c4e156210174edc7f7b953"
 
 [[package]]
 name = "windows_x86_64_msvc"
@@ -5164,9 +5285,15 @@ checksum = "c811ca4a8c853ef420abd8592ba53ddbbac90410fab6903b3e79972a631f7680"
 
 [[package]]
 name = "windows_x86_64_msvc"
-version = "0.42.0"
+version = "0.42.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9aec5da331524158c6d1a4ac0ab1541149c0b9505fde06423b02f5ef0106b9f0"
+
+[[package]]
+name = "windows_x86_64_msvc"
+version = "0.48.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f40009d85759725a34da6d89a94e63d7bdc50a862acf0dbc7c8e488f1edcb6f5"
+checksum = "1a515f5799fe4961cb532f983ce2b23082366b898e52ffbce459c86f67c8378a"
 
 [[package]]
 name = "winreg"
```

### ckb-bin/Cargo.toml
```diff
@@ -42,7 +42,7 @@ base64 = "0.21.0"
 tempfile.workspace = true
 rayon = "1.0"
 sentry = { version = "0.26.0", optional = true }
-atty = "0.2"
+is-terminal = "0.4.7"
 fdlimit = "0.2.1"
 
 [features]
```

### ckb-bin/src/subcommand/migrate.rs
```diff
@@ -1,5 +1,6 @@
 use ckb_app_config::{ExitCode, MigrateArgs};
 use ckb_launcher::migrate::Migrate;
+use is_terminal::IsTerminal;
 use std::cmp::Ordering;
 
 use crate::helper::prompt;
@@ -37,7 +38,7 @@ pub fn migrate(args: MigrateArgs) -> Result<(), ExitCode> {
             }
 
             if migrate.require_expensive(&db) && !args.force {
-                if atty::is(atty::Stream::Stdin) && atty::is(atty::Stream::Stdout) {
+                if std::io::stdin().is_terminal() && std::io::stdout().is_terminal() {
                     let input = prompt("\
                     \n\
                     Doing migration will take quite a long time before CKB could work again.\n\
```

### deny.toml
```diff
@@ -7,7 +7,9 @@ ignore = [
     # TODO Potential segfault in the time crate; waiting for the fix from upstream (chrono)
     "RUSTSEC-2020-0071",
     # TODO Potential segfault in the chrono crate; waiting for the new release of chrono
-    "RUSTSEC-2020-0159"
+    "RUSTSEC-2020-0159",
+    # waiting https://github.com/bheisler/criterion.rs/pull/628 bump release
+    "RUSTSEC-2021-0145"
 ]
 
 [licenses]
```
