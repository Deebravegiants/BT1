# [?] Merge branch 'testnet3' into fix/unecessary-overflow-checks

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2023-10-07
Source: https://github.com/AleoNet/snarkVM-test/commit/b079b8242849b771ba9c91fdcf9a0cd43fcdbb9c
Type: security-commit

## Details
Merge branch 'testnet3' into fix/unecessary-overflow-checks

## Patch
### .cargo/release-version
```diff
@@ -1 +1 @@
-v0.14.6
\ No newline at end of file
+v0.15.1
\ No newline at end of file
```

### .circleci/config.yml
```diff
@@ -645,13 +645,43 @@ jobs:
           workspace_member: synthesizer/program
           cache_key: snarkvm-synthesizer-program-cache
 
-  synthesizer-program-integration:
+  synthesizer-program-integration-keccak:
     docker:
       - image: cimg/rust:1.71.1
     resource_class: 2xlarge
     steps:
       - run_serial:
-          flags: --test '*'
+          flags: keccak --test '*'
+          workspace_member: synthesizer/program
+          cache_key: snarkvm-synthesizer-program-cache
+
+  synthesizer-program-integration-psd:
+    docker:
+      - image: cimg/rust:1.71.1
+    resource_class: 2xlarge
+    steps:
+      - run_serial:
+          flags: psd --test '*'
+          workspace_member: synthesizer/program
+          cache_key: snarkvm-synthesizer-program-cache
+
+  synthesizer-program-integration-sha:
+    docker:
+      - image: cimg/rust:1.71.1
+    resource_class: 2xlarge
+    steps:
+      - run_serial:
+          flags: sha --test '*'
+          workspace_member: synthesizer/program
+          cache_key: snarkvm-synthesizer-program-cache
+
+  synthesizer-program-integration-rest:
+    docker:
+      - image: cimg/rust:1.71.1
+    resource_class: 2xlarge
+    steps:
+      - run_serial:
+          flags: --test '*' -- --skip keccak --skip psd --skip sha
           workspace_member: synthesizer/program
           cache_key: snarkvm-synthesizer-program-cache
 
@@ -822,7 +852,10 @@ workflows:
       - synthesizer-integration
       - synthesizer-process
       - synthesizer-program
-      - synthesizer-program-integration
+      - synthesizer-program-integration-keccak
+      - synthesizer-program-integration-psd
+      - synthesizer-program-integration-sha
+      - synthesizer-program-integration-rest
       - synthesizer-snark
       - utilities
       - utilities-derives
```

### .github/workflows/benchmarks.yml
```diff
@@ -34,7 +34,7 @@ jobs:
           cd algorithms
           cargo bench --bench variable_base -- --output-format bencher | tee -a ../output.txt
           cargo bench --bench poseidon_sponge -- --output-format bencher | tee -a ../output.txt
-          cargo bench --bench marlin -- --output-format bencher | tee -a ../output.txt
+          cargo bench --bench varuna -- --output-format bencher | tee -a ../output.txt
           cd ..
 
       - name: Benchmark circuit/environment
@@ -52,7 +52,8 @@ jobs:
       - name: Benchmark console/algorithms
         run: |
           cd console/algorithms
-          cargo bench --bench poseidon_sponge -- --output-format bencher | tee -a ../../output.txt
+          cargo bench --bench poseidon -- --output-format bencher | tee -a ../../output.txt
+          cargo bench --bench elligator2 -- --output-format bencher | tee -a ../../output.txt
           cd ../..
 
       - name: Benchmark console/collections
```

### .gitignore
```diff
@@ -8,6 +8,8 @@
 *.usrs
 !**/powers-of-beta-15.usrs*
 !**/shifted-powers-of-beta-15.usrs*
+!**/powers-of-beta-16.usrs*
+!**/shifted-powers-of-beta-16.usrs*
 !**/powers-of-beta-gamma.usrs
 !**/beta-h.usrs
 !**/neg-powers-of-beta.usrs
```

### CONTRIBUTING.md
```diff
@@ -14,6 +14,9 @@ Please follow the instructions below when filing a pull request:
 
 snarkVM is a big project, so (non-)adherence to best practices related to performance can have a considerable impact; below are the rules we try to follow at all times in order to ensure high quality of the code:
 
+### Error handling
+- prefer the use of `checked_div` when dividing polynomials.
+
 ### Memory handling
 - if the final size is known, pre-allocate the collections (`Vec`, `HashMap` etc.) using `with_capacity` or `reserve` - this ensures that there are both fewer allocations (which involve system calls) and that the final allocated capacity is as close to the required size as possible
 - create the collections right before they are populated/used, as opposed to e.g. creating a few big ones at the beginning of a function and only using them later on; this reduces the amount of time they occupy memory
```

### Cargo.lock
```diff
@@ -4,9 +4,9 @@ version = 3
 
 [[package]]
 name = "addr2line"
-version = "0.20.0"
+version = "0.21.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f4fa78e18c64fce05e902adecd7a5eed15a5e0a3439f7b0e169f0252214865e3"
+checksum = "8a30b2e23b9e17a9f90641c7ab1549cd9b44f296d3ccbf309d2863cfe398a0cb"
 dependencies = [
  "gimli",
 ]
@@ -30,9 +30,9 @@ dependencies = [
 
 [[package]]
 name = "aho-corasick"
-version = "1.0.4"
+version = "1.0.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6748e8def348ed4d14996fa801f4122cd763fff530258cdc03f64b25f89d3a5a"
+checksum = "0c378d78423fdad8089616f827526ee33c19f2fddbd5de1629152c9593ba4783"
 dependencies = [
  "memchr",
 ]
@@ -120,24 +120,23 @@ checksum = "4b46cbb362ab8752921c97e041f5e366ee6297bd428a31275b9fcf1e380f7299"
 
 [[package]]
 name = "anstream"
-version = "0.3.2"
+version = "0.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0ca84f3628370c59db74ee214b3263d58f9aadd9b4fe7e711fd87dc452b7f163"
+checksum = "b1f58811cfac344940f1a400b6e6231ce35171f614f26439e80f8c1465c5cc0c"
 dependencies = [
  "anstyle",
  "anstyle-parse",
  "anstyle-query",
  "anstyle-wincon",
  "colorchoice",
- "is-terminal",
  "utf8parse",
 ]
 
 [[package]]
 name = "anstyle"
-version = "1.0.1"
+version = "1.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3a30da5c5f2d5e72842e00bcb57657162cdabef0931f40e2deb9b4140440cecd"
+checksum = "b84bf0a05bbb2a83e5eb6fa36bb6e87baa08193c35ff52bbf6b38d8af2890e46"
 
 [[package]]
 name = "anstyle-parse"
@@ -159,9 +158,9 @@ dependencies = [
 
 [[package]]
 name = "anstyle-wincon"
-version = "1.0.2"
+version = "2.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c677ab05e09154296dd37acecd46420c17b9713e8366facafa8fc0885167cf4c"
+checksum = "58f54d10c6dfa51283a066ceab3ec1ab78d13fae00aa49243a45e4571fb79dfd"
 dependencies = [
  "anstyle",
  "windows-sys 0.48.0",
@@ -193,7 +192,7 @@ checksum = "bc00ceb34980c03614e35a3a4e218276a0a824e911d07651cd0d858a51e8c0f0"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -204,9 +203,9 @@ checksum = "d468802bab17cbc0cc575e9b053f41e72aa36bfa6b7f55e3529ffa43161b97fa"
 
 [[package]]
 name = "backtrace"
-version = "0.3.68"
+version = "0.3.69"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4319208da049c43661739c5fade2ba182f09d1dc2299b32298d3a31692b17e12"
+checksum = "2089b7e3f35b9dd2d0ed921ead4f6d318c27680d4a5bd167b3ee120edb105837"
 dependencies = [
  "addr2line",
  "cc",
@@ -219,9 +218,9 @@ dependencies = [
 
 [[package]]
 name = "base64"
-version = "0.21.2"
+version = "0.21.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "604178f6c5c21f02dc555784810edfb88d34ac2c73b2eae109655649ee73ce3d"
+checksum = "414dcefbc63d77c526a76b3afcf6fbb9b5e2791c19c3aa2297733208750c6e53"
 
 [[package]]
 name = "bech32"
@@ -256,7 +255,7 @@ dependencies = [
  "regex",
  "rustc-hash",
  "shlex",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -297,9 +296,9 @@ dependencies = [
 
 [[package]]
 name = "blake2s_simd"
-version = "1.0.1"
+version = "1.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6637f448b9e61dfadbdcbae9a885fadee1f3eaffb1f8d3c1965d3ade8bdfd44f"
+checksum = "94230421e395b9920d23df13ea5d77a20e1725331f90fbbf6df6040b33f756ae"
 dependencies = [
  "arrayref",
  "arrayvec",
@@ -350,9 +349,9 @@ checksum = "14c189c53d098945499cdfa7ecc63567cf3886b3332b312a5b4585d8d3a6a610"
 
 [[package]]
 name = "bytes"
-version = "1.4.0"
+version = "1.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "89b2fd2a0dcf38d7971e2194b6b6eebab45ae01067456a7fd93d5547a61b70be"
+checksum = "a2bd12c1caf447e69cd4528f47f94d203fd2582878ecb9e9465484c4148a8223"
 
 [[package]]
 name = "bzip2-sys"
@@ -456,20 +455,19 @@ dependencies = [
 
 [[package]]
 name = "clap"
-version = "4.3.23"
+version = "4.4.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "03aef18ddf7d879c15ce20f04826ef8418101c7e528014c3eeea13321047dca3"
+checksum = "6a13b88d2c62ff462f88e4a121f17a82c1af05693a2f192b5c38d14de73c19f6"
 dependencies = [
  "clap_builder",
  "clap_derive",
- "once_cell",
 ]
 
 [[package]]
 name = "clap_builder"
-version = "4.3.23"
+version = "4.4.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f8ce6fffb678c9b80a70b6b6de0aad31df727623a70fd9a842c30cd573e2fa98"
+checksum = "2bb9faaa7c2ef94b2743a21f5a29e6f0010dff4caa69ac8e9d6cf8b6fa74da08"
 dependencies = [
  "anstream",
  "anstyle",
@@ -479,21 +477,21 @@ dependencies = [
 
 [[package]]
 name = "clap_derive"
-version = "4.3.12"
+version = "4.4.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "54a9bb5758fc5dfe728d1019941681eccaf0cf8a4189b692a0ee2f2ecf90a050"
+checksum = "0862016ff20d69b84ef8247369fabf5c008a7417002411897d40ee1f4532b873"
 dependencies = [
  "heck",
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
 name = "clap_lex"
-version = "0.5.0"
+version = "0.5.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2da6da31387c7e4ef160ffab6d5e7f00c42626fe39aea70a7b0f1773f7dd6c1b"
+checksum = "cd7cc57abe963c6d3b9d8be5b06ba7c8957a930305ca90304f24ef040aa6f961"
 
 [[package]]
 name = "colorchoice"
@@ -537,9 +535,9 @@ dependencies = [
 
 [[package]]
 name = "constant_time_eq"
-version = "0.2.6"
+version = "0.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "21a53c0a4d288377e7415b53dcfc3c04da5cdc2cc95c8d5ac178b58f0b861ad6"
+checksum = "f7144d30dcf0fafbce74250a3963025d8d52177934239851c917d29f1df280c2"
 
 [[package]]
 name = "core-foundation"
@@ -654,6 +652,12 @@ dependencies = [
  "cfg-if",
 ]
 
+[[package]]
+name = "crunchy"
+version = "0.2.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7a81dae078cea95a014a339291cec439d2f232ebe854a9d672b796c6afafa9b7"
+
 [[package]]
 name = "crypto-common"
 version = "0.1.6"
@@ -714,9 +718,9 @@ dependencies = [
 
 [[package]]
 name = "dashmap"
-version = "5.5.0"
+version = "5.5.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6943ae99c34386c84a470c499d3414f66502a41340aa895406e0d2e4a207b91d"
+checksum = "978747c1d849a7d2ee5e8adc0159961c48fb7e5db2f06af6723b80123bb53856"
 dependencies = [
  "cfg-if",
  "hashbrown 0.14.0",
@@ -863,9 +867,9 @@ checksum = "a246d82be1c9d791c5dfde9a2bd045fc3cbba3fa2b11ad558f27d01712f00569"
 
 [[package]]
 name = "encoding_rs"
-version = "0.8.32"
+version = "0.8.33"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "071a31f4ee85403370b58aca746f01041ede6f0da2730960ad001edc2b71b394"
+checksum = "7268b386296a025e474d5140678f75d6de9493ae55a5d709eeb9dd08149945e1"
 dependencies = [
  "cfg-if",
 ]
@@ -904,9 +908,9 @@ checksum = "5443807d6dff69373d433ab9ef5378ad8df50ca6298caf15de6e52e24aaf54d5"
 
 [[package]]
 name = "errno"
-version = "0.3.2"
+version = "0.3.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6b30f669a7961ef1631673d2766cc92f52d64f7ef354d4fe0ddfd30ed52f0f4f"
+checksum = "136526188508e25c6fef639d7927dfb3e0e3084488bf202267829cf7fc23dbdd"
 dependencies = [
  "errno-dragonfly",
  "libc",
@@ -933,6 +937,15 @@ dependencies = [
  "once_cell",
 ]
 
+[[package]]
+name = "fastrand"
+version = "1.9.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e51093e27b0797c359783294ca4f0a911c270184cb10f85783b118614a1501be"
+dependencies = [
+ "instant",
+]
+
 [[package]]
 name = "fastrand"
 version = "2.0.0"
@@ -1117,9 +1130,9 @@ dependencies = [
 
 [[package]]
 name = "gimli"
-version = "0.27.3"
+version = "0.28.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b6c80984affa11d98d1b88b66ac8853f143217b399d3c74116778ff8fdb4ed2e"
+checksum = "6fb8d784f27acf97159b40fc4db5ecd8aa23b9ad5ef69cdd136d3bc80665f0c0"
 
 [[package]]
 name = "glob"
@@ -1129,9 +1142,9 @@ checksum = "d2fabcfbdc87f4758337ca535fb41a6d701b65693ce38287d856d1674551ec9b"
 
 [[package]]
 name = "h2"
-version = "0.3.20"
+version = "0.3.21"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "97ec8491ebaf99c8eaa73058b045fe58073cd6be7f596ac993ced0b0a0c01049"
+checksum = "91fc23aa11be92976ef4729127f1a74adf36d8436f7816b185d18df956790833"
 dependencies = [
  "bytes",
  "fnv",
@@ -1483,9 +1496,9 @@ dependencies = [
 
 [[package]]
 name = "memchr"
-version = "2.5.0"
+version = "2.6.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2dffe52ecf27772e601905b7522cb4ef790d2cc203488bbd0e2fe85fcb74566d"
+checksum = "8f232d6ef707e1956a43342693d2a31e72989554d58299d7a88738cc95b0d35c"
 
 [[package]]
 name = "memoffset"
@@ -1574,9 +1587,9 @@ dependencies = [
 
 [[package]]
 name = "num-bigint"
-version = "0.4.3"
+version = "0.4.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f93ab6289c7b344a8a9f60f88d80aa20032336fe78da341afc91c8a2341fc75f"
+checksum = "608e7659b5c3d7cba262d894801b9ec9d00de989e8a82bd4bef91d08da45cdc0"
 dependencies = [
  "autocfg",
  "num-integer",
@@ -1591,7 +1604,7 @@ checksum = "9e6a0fd4f737c707bd9086cc16c925f294943eb62eb71499e9fd4cf71f8b9f4e"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -1642,9 +1655,9 @@ checksum = "830b246a0e5f20af87141b25c173cd1b609bd7779a4617d6ec582abaf90870f3"
 
 [[package]]
 name = "object"
-version = "0.31.1"
+version = "0.32.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8bda667d9f2b5051b8833f59f3bf748b28ef54f850f4fcb389a252aa383866d1"
+checksum = "9cf5f9dd3933bd50a9e1f149ec995f39ae2c496d31fd772c1fd45ebc27e902b0"
 dependencies = [
  "memchr",
 ]
@@ -1682,11 +1695,11 @@ dependencies = [
 
 [[package]]
 name = "openssl"
-version = "0.10.56"
+version = "0.10.57"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "729b745ad4a5575dd06a3e1af1414bd330ee561c01b3899eb584baeaa8def17e"
+checksum = "bac25ee399abb46215765b1cb35bc0212377e58a061560d8b29b024fd0430e7c"
 dependencies = [
- "bitflags 1.3.2",
+ "bitflags 2.4.0",
  "cfg-if",
  "foreign-types",
  "libc",
@@ -1703,7 +1716,7 @@ checksum = "a948666b637a0f465e8564c73e89d4dde00d72d4d473cc972f390fc3dcee7d9c"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -1714,9 +1727,9 @@ checksum = "ff011a302c396a5197692431fc1948019154afc178baf7d8e37367442a4601cf"
 
 [[package]]
 name = "openssl-sys"
-version = "0.9.91"
+version = "0.9.93"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "866b5f16f90776b9bb8dc1e1802ac6f0513de3a7a7465867bfbc563dc737faac"
+checksum = "db4d56a4c0478783083cfafcc42493dd4a981d41669da64b4572a2a089b51b1d"
 dependencies = [
  "cc",
  "libc",
@@ -1773,9 +1786,9 @@ checksum = "9b2a4787296e9989611394c33f193f676704af1686e70b8f8033ab5ba9a35a94"
 
 [[package]]
 name = "pin-project-lite"
-version = "0.2.12"
+version = "0.2.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "12cc1b0bf1727a77a54b6654e7b5f1af8604923edc8b81885f8ec92f9e3f0a05"
+checksum = "8afb450f006bf6385ca15ef45d71d2288452bc3683ce2e2cacc0d18e4be60b58"
 
 [[package]]
 name = "pin-utils"
@@ -1819,9 +1832,9 @@ dependencies = [
 
 [[package]]
 name = "portable-atomic"
-version = "1.4.2"
+version = "1.4.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f32154ba0af3a075eefa1eda8bb414ee928f62303a54ea85b8d6638ff1a6ee9e"
+checksum = "31114a898e107c51bb1609ffaf55a0e011cf6a4d7f1170d0015a165082c0338b"
 
 [[package]]
 name = "ppv-lite86"
@@ -1831,12 +1844,12 @@ checksum = "5b40af805b3121feab8a3c29f04d8ad262fa8e0561883e7653e024ae4479e6de"
 
 [[package]]
 name = "prettyplease"
-version = "0.2.12"
+version = "0.2.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6c64d9ba0963cdcea2e1b2230fbae2bab30eb25a174be395c41e764bfb65dd62"
+checksum = "8832c0f9be7e3cae60727e6256cfd2cd3c3e2b6cd5dad4190ecb2fd658c9030b"
 dependencies = [
  "proc-macro2",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -2000,14 +2013,14 @@ dependencies = [
 
 [[package]]
 name = "regex"
-version = "1.9.3"
+version = "1.9.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "81bc1d4caf89fac26a70747fe603c130093b53c773888797a6329091246d651a"
+checksum = "697061221ea1b4a94a624f67d0ae2bfe4e22b8a17b6a192afb11046542cc8c47"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-automata 0.3.6",
- "regex-syntax 0.7.4",
+ "regex-automata 0.3.8",
+ "regex-syntax 0.7.5",
 ]
 
 [[package]]
@@ -2021,13 +2034,13 @@ dependencies = [
 
 [[package]]
 name = "regex-automata"
-version = "0.3.6"
+version = "0.3.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fed1ceff11a1dddaee50c9dc8e4938bd106e9d89ae372f192311e7da498e3b69"
+checksum = "c2f401f4955220693b56f8ec66ee9c78abffd8d1c4f23dc41a23839eb88f0795"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-syntax 0.7.4",
+ "regex-syntax 0.7.5",
 ]
 
 [[package]]
@@ -2038,15 +2051,15 @@ checksum = "f162c6dd7b008981e4d40210aca20b4bd0f9b60ca9271061b07f78537722f2e1"
 
 [[package]]
 name = "regex-syntax"
-version = "0.7.4"
+version = "0.7.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e5ea92a5b6195c6ef2a0295ea818b312502c6fc94dde986c5553242e18fd4ce2"
+checksum = "dbb5fb1acd8a1a18b3dd5be62d25485eb770e05afb408a9627d14d451bae12da"
 
 [[package]]
 name = "reqwest"
-version = "0.11.18"
+version = "0.11.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cde824a14b7c14f85caff81225f411faacc04a2013f41670f41443742b1c1c55"
+checksum = "3e9ad3fe7488d7e34558a2033d45a0c90b72d97b4f80705666fea71472e2e6a1"
 dependencies = [
  "base64",
  "bytes",
@@ -2161,9 +2174,9 @@ dependencies = [
 
 [[package]]
 name = "rustix"
-version = "0.38.8"
+version = "0.38.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "19ed4fa021d81c8392ce04db050a3da9a60299050b7ae1cf482d862b54a7218f"
+checksum = "c0c3dde1fc030af041adc40e79c0e7fbcf431dd24870053d187d7c66e4b87453"
 dependencies = [
  "bitflags 2.4.0",
  "errno",
@@ -2174,31 +2187,31 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.21.6"
+version = "0.21.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1d1feddffcfcc0b33f5c6ce9a29e341e4cd59c3f78e7ee45f4a40c038b1d6cbb"
+checksum = "cd8d6c9f025a446bc4d18ad9632e69aec8f287aa84499ee335599fabd20c3fd8"
 dependencies = [
  "log",
  "ring",
- "rustls-webpki 0.101.3",
+ "rustls-webpki 0.101.4",
  "sct",
 ]
 
 [[package]]
 name = "rustls-webpki"
-version = "0.100.1"
+version = "0.100.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d6207cd5ed3d8dca7816f8f3725513a34609c0c765bf652b8c3cb4cfd87db46b"
+checksum = "e98ff011474fa39949b7e5c0428f9b4937eda7da7848bbb947786b7be0b27dab"
 dependencies = [
  "ring",
  "untrusted",
 ]
 
 [[package]]
 name = "rustls-webpki"
-version = "0.101.3"
+version = "0.101.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "261e9e0888cba427c3316e6322805653c9425240b6fd96cee7cb671ab70ab8d0"
+checksum = "7d93931baf2d282fff8d3a532bbfd7653f734643161b87e3e01e59a04439bf0d"
 dependencies = [
  "ring",
  "untrusted",
@@ -2297,18 +2310,30 @@ dependencies = [
  "libc",
 ]
 
+[[package]]
+name = "self-replace"
+version = "1.3.6"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c56335359191626938ef6fdeb478f9f6a7c6020254d7f4641c7d810369fa0ec1"
+dependencies = [
+ "fastrand 1.9.0",
+ "tempfile",
+ "windows-sys 0.48.0",
+]
+
 [[package]]
 name = "self_update"
-version = "0.37.0"
+version = "0.38.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a667e18055120bcc9a658d55d36f2f6bfc82e07968cc479ee7774e3bfb501e14"
+checksum = "2b3c585a1ced6b97ac13bd5e56f66559e5a75f477da5913f70df98e114518446"
 dependencies = [
  "hyper",
  "indicatif",
  "log",
  "quick-xml",
  "regex",
  "reqwest",
+ "self-replace",
  "semver",
  "serde_json",
  "tempfile",
@@ -2323,29 +2348,29 @@ checksum = "b0293b4b29daaf487284529cc2f5675b8e57c61f70167ba415a463651fd6a918"
 
 [[package]]
 name = "serde"
-version = "1.0.185"
+version = "1.0.188"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "be9b6f69f1dfd54c3b568ffa45c310d6973a5e5148fd40cf515acaf38cf5bc31"
+checksum = "cf9e0fcba69a370eed61bcf2b728575f726b50b55cba78064753d708ddc7549e"
 dependencies = [
  "serde_derive",
 ]
 
 [[package]]
 name = "serde_derive"
-version = "1.0.185"
+version = "1.0.188"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dc59dfdcbad1437773485e0367fea4b090a2e0a16d9ffc46af47764536a298ec"
+checksum = "4eca7ac642d82aa35b60049a6eccb4be6be75e599bd2e9adb5f875a737654af2"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
 name = "serde_json"
-version = "1.0.105"
+version = "1.0.106"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "693151e1ac27563d6dbcec9dee9fbd5da8539b20fa14ad3752b2e6d363ace360"
+checksum = "2cc66a619ed80bf7a0f6b17dd063a84b88f6dea1813737cf469aef1d081142c2"
 dependencies = [
  "indexmap 2.0.0",
  "itoa",
@@ -2400,7 +2425,7 @@ checksum = "91d129178576168c589c9ec973feedf7d3126c01ac2bf08795109aa35b69fb8f"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -2425,15 +2450,15 @@ dependencies = [
 
 [[package]]
 name = "shlex"
-version = "1.1.0"
+version = "1.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "43b2853a4d09f215c24cc5489c992ce46052d359b5109343cbafbf26bc62f8a3"
+checksum = "a7cee0529a6d40f580e7a5e6c495c8fbfe21b7b52795ed4bb5e62cdf92bc6380"
 
 [[package]]
 name = "slab"
-version = "0.4.8"
+version = "0.4.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6528351c9bc8ab22353f9d776db39a20288e8d6c37ef8cfe3317cf875eecfc2d"
+checksum = "8f92a496fb766b417c996b9c5e57daf2f7ad3b0bebe1ccfca4856390e3d3bb67"
 dependencies = [
  "autocfg",
 ]
@@ -2444,9 +2469,18 @@ version = "1.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "62bb4feee49fdd9f707ef802e22365a35de4b7b299de4763d44bfea899442ff9"
 
+[[package]]
+name = "smol_str"
+version = "0.2.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "74212e6bbe9a4352329b2f68ba3130c15a3f26fe88ff22dbdc6cdd58fa85e99c"
+dependencies = [
+ "serde",
+]
+
 [[package]]
 name = "snarkvm"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "anstyle",
  "anyhow",
@@ -2481,7 +2515,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-algorithms"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
  "anyhow",
@@ -2497,6 +2531,7 @@ dependencies = [
  "indexmap 2.0.0",
  "itertools 0.11.0",
  "lazy_static",
+ "num-traits",
  "parking_lot",
  "rand",
  "rand_chacha",
@@ -2519,7 +2554,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-algorithms-cuda"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "blst",
  "cc",
@@ -2529,7 +2564,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-circuit-account",
  "snarkvm-circuit-algorithms",
@@ -2542,7 +2577,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-account"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "anyhow",
  "snarkvm-circuit-algorithms",
@@ -2554,7 +2589,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-algorithms"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "anyhow",
  "snarkvm-circuit-types",
@@ -2566,7 +2601,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-collections"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "anyhow",
  "snarkvm-circuit-algorithms",
@@ -2580,14 +2615,15 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-environment"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "criterion",
  "indexmap 2.0.0",
  "itertools 0.11.0",
  "nom",
  "num-traits",
  "once_cell",
+ "serial_test",
  "snarkvm-algorithms",
  "snarkvm-circuit",
  "snarkvm-circuit-environment-witness",
@@ -2600,11 +2636,11 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-environment-witness"
-version = "0.14.6"
+version = "0.15.1"
 
 [[package]]
 name = "snarkvm-circuit-network"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-circuit-algorithms",
  "snarkvm-circuit-collections",
@@ -2615,22 +2651,25 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-program"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "anyhow",
+ "paste",
  "rand",
  "snarkvm-circuit-account",
+ "snarkvm-circuit-algorithms",
  "snarkvm-circuit-collections",
  "snarkvm-circuit-network",
  "snarkvm-circuit-types",
+ "snarkvm-console",
  "snarkvm-console-account",
  "snarkvm-console-program",
  "snarkvm-utilities",
 ]
 
 [[package]]
 name = "snarkvm-circuit-types"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-circuit-environment",
  "snarkvm-circuit-types-address",
@@ -2640,11 +2679,12 @@ dependencies = [
  "snarkvm-circuit-types-integers",
  "snarkvm-circuit-types-scalar",
  "snarkvm-circuit-types-string",
+ "snarkvm-console",
 ]
 
 [[package]]
 name = "snarkvm-circuit-types-address"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-circuit-environment",
  "snarkvm-circuit-types-boolean",
@@ -2656,7 +2696,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-types-boolean"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "criterion",
  "snarkvm-circuit-environment",
@@ -2665,7 +2705,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-types-field"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-circuit-environment",
  "snarkvm-circuit-types-boolean",
@@ -2674,7 +2714,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-types-group"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-circuit-environment",
  "snarkvm-circuit-types-boolean",
@@ -2686,19 +2726,20 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-types-integers"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "paste",
  "snarkvm-circuit-environment",
  "snarkvm-circuit-types-boolean",
  "snarkvm-circuit-types-field",
+ "snarkvm-circuit-types-scalar",
  "snarkvm-console-types-integers",
  "snarkvm-utilities",
 ]
 
 [[package]]
 name = "snarkvm-circuit-types-scalar"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-circuit-environment",
  "snarkvm-circuit-types-boolean",
@@ -2708,7 +2749,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-circuit-types-string"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "rand",
  "snarkvm-circuit-environment",
@@ -2721,7 +2762,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-console-account",
  "snarkvm-console-algorithms",
@@ -2733,7 +2774,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-account"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "bs58",
@@ -2745,7 +2786,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-algorithms"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "blake2s_simd",
  "criterion",
@@ -2758,11 +2799,12 @@ dependencies = [
  "snarkvm-curves",
  "snarkvm-fields",
  "snarkvm-utilities",
+ "tiny-keccak",
 ]
 
 [[package]]
 name = "snarkvm-console-collections"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
  "criterion",
@@ -2775,7 +2817,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-network"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "anyhow",
  "indexmap 2.0.0",
@@ -2797,7 +2839,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-network-environment"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "anyhow",
  "bech32",
@@ -2813,7 +2855,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-program"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "enum_index",
@@ -2822,8 +2864,10 @@ dependencies = [
  "num-derive",
  "num-traits",
  "once_cell",
+ "paste",
  "serde_json",
  "snarkvm-console-account",
+ "snarkvm-console-algorithms",
  "snarkvm-console-collections",
  "snarkvm-console-network",
  "snarkvm-console-types",
@@ -2832,7 +2876,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-types"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-console-network-environment",
  "snarkvm-console-types-address",
@@ -2846,7 +2890,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-types-address"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "serde_json",
@@ -2858,7 +2902,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-types-boolean"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "serde_json",
@@ -2867,7 +2911,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-types-field"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "serde_json",
@@ -2877,7 +2921,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-types-group"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "serde_json",
@@ -2889,18 +2933,19 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-types-integers"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "serde_json",
  "snarkvm-console-network-environment",
  "snarkvm-console-types-boolean",
  "snarkvm-console-types-field",
+ "snarkvm-console-types-scalar",
 ]
 
 [[package]]
 name = "snarkvm-console-types-scalar"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "serde_json",
@@ -2911,7 +2956,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-console-types-string"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "serde_json",
@@ -2923,7 +2968,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-curves"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "criterion",
@@ -2938,7 +2983,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-fields"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
  "anyhow",
@@ -2954,7 +2999,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
  "anyhow",
@@ -2980,7 +3025,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-authority"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "anyhow",
  "bincode",
@@ -2993,7 +3038,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-block"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "indexmap 2.0.0",
@@ -3016,14 +3061,14 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-coinbase"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
  "anyhow",
  "bincode",
  "blake2",
  "criterion",
- "itertools 0.11.0",
+ "indexmap 2.0.0",
  "rand",
  "rayon",
  "serde_json",
@@ -3037,7 +3082,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-committee"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "anyhow",
  "bincode",
@@ -3056,7 +3101,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-narwhal"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "snarkvm-ledger-narwhal",
  "snarkvm-ledger-narwhal-batch-certificate",
@@ -3069,7 +3114,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-narwhal-batch-certificate"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "indexmap 2.0.0",
@@ -3083,7 +3128,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-narwhal-batch-header"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "indexmap 2.0.0",
@@ -3096,7 +3141,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-narwhal-data"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bytes",
  "serde_json",
@@ -3106,7 +3151,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-narwhal-subdag"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "indexmap 2.0.0",
@@ -3119,7 +3164,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-narwhal-transmission"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "bytes",
@@ -3132,7 +3177,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-narwhal-transmission-id"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "serde_json",
@@ -3142,7 +3187,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-query"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "async-trait",
  "reqwest",
@@ -3154,7 +3199,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-store"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
  "anyhow",
@@ -3171,6 +3216,7 @@ dependencies = [
  "snarkvm-ledger-block",
  "snarkvm-ledger-coinbase",
  "snarkvm-ledger-committee",
+ "snarkvm-ledger-narwhal-batch-certificate",
  "snarkvm-ledger-test-helpers",
  "snarkvm-synthesizer-program",
  "snarkvm-synthesizer-snark",
@@ -3181,7 +3227,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-ledger-test-helpers"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "once_cell",
  "snarkvm-circuit",
@@ -3195,7 +3241,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-parameters"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
  "anyhow",
@@ -3227,7 +3273,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-synthesizer"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
  "anyhow",
@@ -3256,15 +3302,17 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-synthesizer-process"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
+ "bincode",
  "colored",
  "indexmap 2.0.0",
  "once_cell",
  "parking_lot",
  "rand",
  "rayon",
+ "serde_json",
  "snarkvm-circuit",
  "snarkvm-console",
  "snarkvm-ledger-block",
@@ -3278,7 +3326,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-synthesizer-program"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "indexmap 2.0.0",
@@ -3293,7 +3341,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-synthesizer-snark"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "bincode",
  "colored",
@@ -3306,7 +3354,7 @@ dependencies = [
 
 [[package]]
 name = "snarkvm-utilities"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "aleo-std",
  "anyhow",
@@ -3318,22 +3366,23 @@ dependencies = [
  "rayon",
  "serde",
  "serde_json",
+ "smol_str",
  "snarkvm-utilities-derives",
  "thiserror",
 ]
 
 [[package]]
 name = "snarkvm-utilities-derives"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
 name = "snarkvm-wasm"
-version = "0.14.6"
+version = "0.15.1"
 dependencies = [
  "getrandom",
  "rand",
@@ -3375,9 +3424,9 @@ checksum = "6e63cff320ae2c57904679ba7cb63280a3dc4613885beafb148ee7bf9aa9042d"
 
 [[package]]
 name = "sppark"
-version = "0.1.3"
+version = "0.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cfb9486baeb35ca1197c4df27451d4df5bd321e15da94c1ddb89670f9e94896a"
+checksum = "ba7a6d98937866ea8917015cd4a72d56d6e7feee8979dbccf83fc0c870053c46"
 dependencies = [
  "cc",
  "which",
@@ -3398,7 +3447,7 @@ dependencies = [
  "proc-macro2",
  "quote 1.0.33",
  "structmeta-derive",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -3409,7 +3458,7 @@ checksum = "a60bcaff7397072dca0017d1db428e30d5002e00b6847703e2e42005c95fbe00"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -3442,9 +3491,9 @@ dependencies = [
 
 [[package]]
 name = "syn"
-version = "2.0.29"
+version = "2.0.32"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c324c494eba9d92503e6f1ef2e6df781e78f6a7705a0202d9801b198807d518a"
+checksum = "239814284fd6f1a4ffe4ca893952cdd93c224b6a1571c9a9eadd670295c0c9e2"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
@@ -3462,9 +3511,9 @@ dependencies = [
 
 [[package]]
 name = "temp-env"
-version = "0.3.4"
+version = "0.3.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9547444bfe52cbd79515c6c8087d8ae6ca8d64d2d31a27746320f5cb81d1a15c"
+checksum = "e010429b1f3ea1311190c658c7570100f03c1dab05c16cfab774181c648d656a"
 dependencies = [
  "parking_lot",
 ]
@@ -3476,7 +3525,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cb94d2f3cc536af71caac6b6fcebf65860b347e7ce0cc9ebe8f70d3e521054ef"
 dependencies = [
  "cfg-if",
- "fastrand",
+ "fastrand 2.0.0",
  "redox_syscall 0.3.5",
  "rustix",
  "windows-sys 0.48.0",
@@ -3491,27 +3540,27 @@ dependencies = [
  "proc-macro2",
  "quote 1.0.33",
  "structmeta",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
 name = "thiserror"
-version = "1.0.47"
+version = "1.0.48"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "97a802ec30afc17eee47b2855fc72e0c4cd62be9b4efe6591edde0ec5bd68d8f"
+checksum = "9d6d7a740b8a666a7e828dd00da9c0dc290dff53154ea77ac109281de90589b7"
 dependencies = [
  "thiserror-impl",
 ]
 
 [[package]]
 name = "thiserror-impl"
-version = "1.0.47"
+version = "1.0.48"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6bb623b56e39ab7dcd4b1b98bb6c8f8d907ed255b18de254088016b27a8ee19b"
+checksum = "49922ecae66cc8a249b77e68d1d0623c1b2c514f0060c27cdc68bd62a1219d35"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -3535,9 +3584,9 @@ dependencies = [
 
 [[package]]
 name = "time"
-version = "0.3.25"
+version = "0.3.28"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b0fdd63d58b18d663fbdf70e049f00a22c8e42be082203be7f26589213cd75ea"
+checksum = "17f6bb557fd245c28e6411aa56b6403c689ad95061f50e4be16c274e70a17e48"
 dependencies = [
  "deranged",
  "serde",
@@ -3550,6 +3599,15 @@ version = "0.1.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7300fbefb4dadc1af235a9cef3737cea692a9d97e1b9cbcd4ebdae6f8868e6fb"
 
+[[package]]
+name = "tiny-keccak"
+version = "2.0.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "2c9d3793400a45f954c52e73d068316d76b6f4e36977e3fcebb13a2721e80237"
+dependencies = [
+ "crunchy",
+]
+
 [[package]]
 name = "tinytemplate"
 version = "1.2.1"
@@ -3650,7 +3708,7 @@ checksum = "5f4f31f56159e98206da9efd823404b79b6ef3143b4a7ab76e67b1751b25a4ab"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
 
 [[package]]
@@ -3789,7 +3847,7 @@ dependencies = [
  "log",
  "once_cell",
  "rustls",
- "rustls-webpki 0.100.1",
+ "rustls-webpki 0.100.2",
  "serde",
  "serde_json",
  "url",
@@ -3798,9 +3856,9 @@ dependencies = [
 
 [[package]]
 name = "url"
-version = "2.4.0"
+version = "2.4.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "50bff7831e19200a85b17131d085c25d7811bc4e186efdaf54bbd132994a88cb"
+checksum = "143b538f18257fac9cad154828a57c6bf5157e1aa604d4816b5995bf6de87ae5"
 dependencies = [
  "form_urlencoded",
  "idna",
@@ -3848,9 +3906,9 @@ dependencies = [
 
 [[package]]
 name = "walkdir"
-version = "2.3.3"
+version = "2.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "36df944cda56c7d8d8b7496af378e6b16de9284591917d307c9b4d313c44e698"
+checksum = "d71d857dc86794ca4c280d616f7da00d2dbfd8cd788846559a6813e6aa4b54ee"
 dependencies = [
  "same-file",
  "winapi-util",
@@ -3894,7 +3952,7 @@ dependencies = [
  "once_cell",
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
  "wasm-bindgen-shared",
 ]
 
@@ -3928,7 +3986,7 @@ checksum = "54681b18a46765f095758388f2d0cf16eb8d4169b639ab575a8f5693af210c7b"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
  "wasm-bindgen-backend",
  "wasm-bindgen-shared",
 ]
@@ -3979,18 +4037,19 @@ version = "0.23.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b03058f88386e5ff5310d9111d53f48b17d732b401aeb83a8d5190f2ac459338"
 dependencies = [
- "rustls-webpki 0.100.1",
+ "rustls-webpki 0.100.2",
 ]
 
 [[package]]
 name = "which"
-version = "4.4.0"
+version = "4.4.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2441c784c52b289a054b7201fc93253e288f094e2f4be9058343127c4226a269"
+checksum = "87ba24419a2078cd2b0f2ede2691b6c66d8e47836da3b6db8265ebad47afbfc7"
 dependencies = [
  "either",
- "libc",
+ "home",
  "once_cell",
+ "rustix",
 ]
 
 [[package]]
@@ -4158,11 +4217,12 @@ checksum = "ed94fce61571a4006852b7389a063ab983c02eb1bb37b47f8272ce92d06d9538"
 
 [[package]]
 name = "winreg"
-version = "0.10.1"
+version = "0.50.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "80d0f4e272c85def139476380b12f9ac60926689dd2e01d4923222f40580869d"
+checksum = "524e57b2c537c0f9b1e69f1965311ec12182b4122e45035b1508cd24d2adadb1"
 dependencies = [
- "winapi",
+ "cfg-if",
+ "windows-sys 0.48.0",
 ]
 
 [[package]]
@@ -4182,5 +4242,5 @@ checksum = "ce36e65b0d2999d2aafac989fb249189a141aee1f53c612c1f37d72631959f69"
 dependencies = [
  "proc-macro2",
  "quote 1.0.33",
- "syn 2.0.29",
+ "syn 2.0.32",
 ]
```

### Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name = "snarkvm"
-version = "0.14.6"
+version = "0.15.1"
 authors = [ "The Aleo Team <hello@aleo.org>" ]
 description = "A decentralized virtual machine"
 homepage = "https://aleo.org"
@@ -22,7 +22,7 @@ categories = [
 include = [ "Cargo.toml", "vm", "README.md", "LICENSE.md" ]
 license = "Apache-2.0"
 edition = "2021"
-rust-version = "1.66"
+rust-version = "1.70"
 
 [workspace]
 members = [
@@ -146,53 +146,53 @@ wasm = [ "snarkvm-wasm" ]
 
 [dependencies.snarkvm-algorithms]
 path = "./algorithms"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.snarkvm-circuit]
 path = "./circuit"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.snarkvm-console]
 path = "./console"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.snarkvm-curves]
 path = "./curves"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.snarkvm-fields]
 path = "./fields"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.snarkvm-ledger]
 path = "./ledger"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.snarkvm-parameters]
 path = "./parameters"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.snarkvm-synthesizer]
 path = "./synthesizer"
-version = "=0.14.6"
+version = "=0.15.1"
 default-features = false
 optional = true
 
 [dependencies.snarkvm-utilities]
 path = "./utilities"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.snarkvm-wasm]
 path = "./wasm"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.anstyle]
@@ -203,8 +203,8 @@ version = "1.0.73"
 optional = true
 
 [dependencies.clap]
-version = "4.3"
-features = [ "derive", "color", "unstable-styles" ]
+version = "4.4"
+features = [ "derive", "color" ]
 optional = true
 
 [dependencies.colored]
@@ -236,7 +236,7 @@ optional = true
 version = "1"
 
 [dependencies.self_update]
-version = "0.37"
+version = "0.38"
 optional = true
 
 [dependencies.serde_json]
```

### algorithms/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name = "snarkvm-algorithms"
-version = "0.14.6"
+version = "0.15.1"
 authors = [ "The Aleo Team <hello@aleo.org>" ]
 description = "Algorithms for a decentralized virtual machine"
 homepage = "https://aleo.org"
@@ -40,33 +40,33 @@ harness = false
 bench = false
 
 [[bench]]
-name = "marlin"
-path = "benches/snark/marlin.rs"
+name = "varuna"
+path = "benches/snark/varuna.rs"
 harness = false
 
 [dependencies.snarkvm-curves]
 path = "../curves"
-version = "=0.14.6"
+version = "=0.15.1"
 default-features = false
 
 [dependencies.snarkvm-fields]
 path = "../fields"
-version = "=0.14.6"
+version = "=0.15.1"
 default-features = false
 
 [dependencies.snarkvm-parameters]
 path = "../parameters"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.snarkvm-utilities]
 path = "../utilities"
-version = "=0.14.6"
+version = "=0.15.1"
 default-features = false
 
 [dependencies.snarkvm-algorithms-cuda]
 path = "./cuda"
-version = "=0.14.6"
+version = "=0.15.1"
 optional = true
 
 [dependencies.aleo-std]
@@ -152,6 +152,9 @@ version = "1.0"
 version = "0.4"
 optional = true
 
+[dependencies.num-traits]
+version = "0.2"
+
 [dev-dependencies.expect-test]
 version = "1.4.1"
 
```

### algorithms/benches/snark/varuna.rs
```diff
@@ -17,7 +17,7 @@ extern crate criterion;
 
 use snarkvm_algorithms::{
     crypto_hash::PoseidonSponge,
-    snark::marlin::{ahp::AHPForR1CS, CircuitVerifyingKey, MarlinHidingMode, MarlinSNARK, TestCircuit},
+    snark::varuna::{ahp::AHPForR1CS, CircuitVerifyingKey, TestCircuit, VarunaHidingMode, VarunaSNARK},
     AlgebraicSponge,
     SNARK,
 };
@@ -27,32 +27,32 @@ use snarkvm_utilities::{CanonicalDeserialize, CanonicalSerialize, TestRng};
 use criterion::Criterion;
 use std::collections::BTreeMap;
 
-type MarlinInst = MarlinSNARK<Bls12_377, FS, MarlinHidingMode>;
+type VarunaInst = VarunaSNARK<Bls12_377, FS, VarunaHidingMode>;
 type FS = PoseidonSponge<Fq, 2, 1>;
 
 fn snark_universal_setup(c: &mut Criterion) {
-    let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(1000000, 1000000, 1000000).unwrap();
+    let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(1000000, 1000000, 1000000).unwrap();
 
     c.bench_function("snark_universal_setup", move |b| {
         b.iter(|| {
-            MarlinInst::universal_setup(max_degree).unwrap();
+            VarunaInst::universal_setup(max_degree).unwrap();
         })
     });
 }
 
 fn snark_circuit_setup(c: &mut Criterion) {
     let rng = &mut TestRng::default();
 
-    let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(100000, 100000, 100000).unwrap();
-    let universal_srs = MarlinInst::universal_setup(max_degree).unwrap();
+    let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(100000, 100000, 100000).unwrap();
+    let universal_srs = VarunaInst::universal_setup(max_degree).unwrap();
 
     for size in [100, 1_000, 10_000] {
         let num_constraints = size;
         let num_variables = size;
         let mul_depth = 1;
         let (circuit, _) = TestCircuit::gen_rand(mul_depth, num_constraints, num_variables, rng);
         c.bench_function(&format!("snark_circuit_setup_{size}"), |b| {
-            b.iter(|| MarlinInst::circuit_setup(&universal_srs, &circuit).unwrap())
+            b.iter(|| VarunaInst::circuit_setup(&universal_srs, &circuit).unwrap())
         });
     }
 }
@@ -64,15 +64,15 @@ fn snark_prove(c: &mut Criterion) {
         let mul_depth = 1;
         let rng = &mut TestRng::default();
 
-        let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(1000, 1000, 1000).unwrap();
-        let universal_srs = MarlinInst::universal_setup(max_degree).unwrap();
+        let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(1000, 1000, 1000).unwrap();
+        let universal_srs = VarunaInst::universal_setup(max_degree).unwrap();
         let universal_prover = &universal_srs.to_universal_prover().unwrap();
         let fs_parameters = FS::sample_parameters();
 
         let (circuit, _) = TestCircuit::gen_rand(mul_depth, num_constraints, num_variables, rng);
 
-        let params = MarlinInst::circuit_setup(&universal_srs, &circuit).unwrap();
-        b.iter(|| MarlinInst::prove(universal_prover, &fs_parameters, &params.0, &circuit, rng).unwrap())
+        let params = VarunaInst::circuit_setup(&universal_srs, &circuit).unwrap();
+        b.iter(|| VarunaInst::prove(universal_prover, &fs_parameters, &params.0, &circuit, rng).unwrap())
     });
 }
 
@@ -83,8 +83,8 @@ fn snark_batch_prove(c: &mut Criterion) {
         let mul_depth_base = 1;
         let rng = &mut TestRng::default();
 
-        let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(1000000, 1000000, 1000000).unwrap();
-        let universal_srs = MarlinInst::universal_setup(max_degree).unwrap();
+        let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(1000000, 1000000, 1000000).unwrap();
+        let universal_srs = VarunaInst::universal_setup(max_degree).unwrap();
         let universal_prover = &universal_srs.to_universal_prover().unwrap();
         let fs_parameters = FS::sample_parameters();
 
@@ -105,7 +105,7 @@ fn snark_batch_prove(c: &mut Criterion) {
                 let (circuit, _) = TestCircuit::gen_rand(mul_depth, num_constraints, num_variables, rng);
                 circuits.push(circuit);
             }
-            let (pk, _) = MarlinInst::circuit_setup(&universal_srs, &circuits[0]).unwrap();
+            let (pk, _) = VarunaInst::circuit_setup(&universal_srs, &circuits[0]).unwrap();
             pks.push(pk);
             all_circuits.push(circuits);
         }
@@ -114,7 +114,7 @@ fn snark_batch_prove(c: &mut Criterion) {
             keys_to_constraints.insert(&pks[i], all_circuits[i].as_slice());
         }
 
-        b.iter(|| MarlinInst::prove_batch(universal_prover, &fs_parameters, &keys_to_constraints, rng).unwrap())
+        b.iter(|| VarunaInst::prove_batch(universal_prover, &fs_parameters, &keys_to_constraints, rng).unwrap())
     });
 }
 
@@ -125,20 +125,20 @@ fn snark_verify(c: &mut Criterion) {
         let mul_depth = 1;
         let rng = &mut TestRng::default();
 
-        let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(100, 100, 100).unwrap();
-        let universal_srs = MarlinInst::universal_setup(max_degree).unwrap();
+        let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(100, 100, 100).unwrap();
+        let universal_srs = VarunaInst::universal_setup(max_degree).unwrap();
         let universal_prover = &universal_srs.to_universal_prover().unwrap();
         let universal_verifier = &universal_srs.to_universal_verifier().unwrap();
         let fs_parameters = FS::sample_parameters();
 
         let (circuit, public_inputs) = TestCircuit::gen_rand(mul_depth, num_constraints, num_variables, rng);
 
-        let (pk, vk) = MarlinInst::circuit_setup(&universal_srs, &circuit).unwrap();
+        let (pk, vk) = VarunaInst::circuit_setup(&universal_srs, &circuit).unwrap();
 
-        let proof = MarlinInst::prove(universal_prover, &fs_parameters, &pk, &circuit, rng).unwrap();
+        let proof = VarunaInst::prove(universal_prover, &fs_parameters, &pk, &circuit, rng).unwrap();
         b.iter(|| {
             let verification =
-                MarlinInst::verify(universal_verifier, &fs_parameters, &vk, public_inputs.as_slice(), &proof).unwrap();
+                VarunaInst::verify(universal_verifier, &fs_parameters, &vk, public_inputs.as_slice(), &proof).unwrap();
             assert!(verification);
         })
     });
@@ -150,8 +150,8 @@ fn snark_batch_verify(c: &mut Criterion) {
         let num_variables_base = 25;
         let rng = &mut TestRng::default();
 
-        let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(1000, 1000, 100).unwrap();
-        let universal_srs = MarlinInst::universal_setup(max_degree).unwrap();
+        let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(1000, 1000, 100).unwrap();
+        let universal_srs = VarunaInst::universal_setup(max_degree).unwrap();
         let universal_prover = &universal_srs.to_universal_prover().unwrap();
         let universal_verifier = &universal_srs.to_universal_verifier().unwrap();
         let fs_parameters = FS::sample_parameters();
@@ -176,7 +176,7 @@ fn snark_batch_verify(c: &mut Criterion) {
                 circuits.push(circuit);
                 inputs.push(public_inputs);
             }
-            let (pk, vk) = MarlinInst::circuit_setup(&universal_srs, &circuits[0]).unwrap();
+            let (pk, vk) = VarunaInst::circuit_setup(&universal_srs, &circuits[0]).unwrap();
             pks.push(pk);
             vks.push(vk);
             all_circuits.push(circuits);
@@ -188,10 +188,10 @@ fn snark_batch_verify(c: &mut Criterion) {
             keys_to_inputs.insert(&vks[i], all_inputs[i].as_slice());
         }
 
-        let proof = MarlinInst::prove_batch(universal_prover, &fs_parameters, &keys_to_constraints, rng).unwrap();
+        let proof = VarunaInst::prove_batch(universal_prover, &fs_parameters, &keys_to_constraints, rng).unwrap();
         b.iter(|| {
             let verification =
-                MarlinInst::verify_batch(universal_verifier, &fs_parameters, &keys_to_inputs, &proof).unwrap();
+                VarunaInst::verify_batch(universal_verifier, &fs_parameters, &keys_to_inputs, &proof).unwrap();
             assert!(verification);
         })
     });
@@ -210,11 +210,11 @@ fn snark_vk_serialize(c: &mut Criterion) {
         let mul_depth = 1;
         let rng = &mut TestRng::default();
 
-        let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(100, 100, 100).unwrap();
-        let universal_srs = MarlinInst::universal_setup(max_degree).unwrap();
+        let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(100, 100, 100).unwrap();
+        let universal_srs = VarunaInst::universal_setup(max_degree).unwrap();
         let (circuit, _) = TestCircuit::gen_rand(mul_depth, num_constraints, num_variables, rng);
 
-        let (_, vk) = MarlinInst::circuit_setup(&universal_srs, &circuit).unwrap();
+        let (_, vk) = VarunaInst::circuit_setup(&universal_srs, &circuit).unwrap();
         let mut bytes = Vec::with_capacity(10000);
         group.bench_function(name, |b| {
             b.iter(|| {
@@ -245,11 +245,11 @@ fn snark_vk_deserialize(c: &mut Criterion) {
             let mul_depth = 1;
             let rng = &mut TestRng::default();
 
-            let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(100, 100, 100).unwrap();
-            let universal_srs = MarlinInst::universal_setup(max_degree).unwrap();
+            let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(100, 100, 100).unwrap();
+            let universal_srs = VarunaInst::universal_setup(max_degree).unwrap();
             let (circuit, _) = TestCircuit::gen_rand(mul_depth, num_constraints, num_variables, rng);
 
-            let (_, vk) = MarlinInst::circuit_setup(&universal_srs, &circuit).unwrap();
+            let (_, vk) = VarunaInst::circuit_setup(&universal_srs, &circuit).unwrap();
             let mut bytes = Vec::with_capacity(10000);
             vk.serialize_with_mode(&mut bytes, compress).unwrap();
             group.bench_function(name, |b| {
@@ -266,8 +266,8 @@ fn snark_vk_deserialize(c: &mut Criterion) {
 fn snark_certificate_prove(c: &mut Criterion) {
     let rng = &mut TestRng::default();
 
-    let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(100000, 100000, 100000).unwrap();
-    let universal_srs = MarlinInst::universal_setup(max_degree).unwrap();
+    let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(100000, 100000, 100000).unwrap();
+    let universal_srs = VarunaInst::universal_setup(max_degree).unwrap();
     let universal_prover = &universal_srs.to_universal_prover().unwrap();
     let fs_parameters = FS::sample_parameters();
     let fs_p = &fs_parameters;
@@ -278,18 +278,18 @@ fn snark_certificate_prove(c: &mut Criterion) {
             let num_variables = size;
             let mul_depth = 1;
             let (circuit, _) = TestCircuit::gen_rand(mul_depth, num_constraints, num_variables, rng);
-            let (pk, vk) = MarlinInst::circuit_setup(&universal_srs, &circuit).unwrap();
+            let (pk, vk) = VarunaInst::circuit_setup(&universal_srs, &circuit).unwrap();
 
-            b.iter(|| MarlinInst::prove_vk(universal_prover, fs_p, &vk, &pk).unwrap())
+            b.iter(|| VarunaInst::prove_vk(universal_prover, fs_p, &vk, &pk).unwrap())
         });
     }
 }
 
 fn snark_certificate_verify(c: &mut Criterion) {
     let rng = &mut TestRng::default();
 
-    let max_degree = AHPForR1CS::<Fr, MarlinHidingMode>::max_degree(100_000, 100_000, 100_000).unwrap();
-    let universal_srs = MarlinInst::universal_setup(max_degree).unwrap();
+    let max_degree = AHPForR1CS::<Fr, VarunaHidingMode>::max_degree(100_000, 100_000, 100_000).unwrap();
+    let universal_srs = VarunaInst::universal_setup(max_degree).unwrap();
     let universal_prover = &universal_srs.to_universal_prover().unwrap();
     let universal_verifier = &universal_srs.to_universal_verifier().unwrap();
     let fs_parameters = FS::sample_parameters();
@@ -301,18 +301,18 @@ fn snark_certificate_verify(c: &mut Criterion) {
             let num_variables = size;
             let mul_depth = 1;
             let (circuit, _) = TestCircuit::gen_rand(mul_depth, num_constraints, num_variables, rng);
-            let (pk, vk) = MarlinInst::circuit_setup(&universal_srs, &circuit).unwrap();
-            let certificate = MarlinInst::prove_vk(universal_prover, fs_p, &vk, &pk).unwrap();
+            let (pk, vk) = VarunaInst::circuit_setup(&universal_srs, &circuit).unwrap();
+            let certificate = VarunaInst::prove_vk(universal_prover, fs_p, &vk, &pk).unwrap();
 
-            b.iter(|| MarlinInst::verify_vk(universal_verifier, fs_p, &circuit, &vk, &certificate).unwrap())
+            b.iter(|| VarunaInst::verify_vk(universal_verifier, fs_p, &circuit, &vk, &certificate).unwrap())
         });
     }
 }
 
 criterion_group! {
-    name = marlin_snark;
+    name = varuna_snark;
     config = Criterion::default().sample_size(10);
     targets = snark_universal_setup, snark_circuit_setup, snark_prove, snark_verify, snark_batch_prove, snark_batch_verify, snark_vk_serialize, snark_vk_deserialize, snark_certificate_prove, snark_certificate_verify,
 }
 
-criterion_main!(marlin_snark);
+criterion_main!(varuna_snark);
```

### algorithms/cuda/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name = "snarkvm-algorithms-cuda"
-version = "0.14.6"
+version = "0.15.1"
 authors = [ "The Aleo Team <hello@aleo.org>" ]
 description = "Cuda optimizations for a decentralized virtual machine"
 homepage = "https://aleo.org"
@@ -33,7 +33,7 @@ version = "0.3.11"
 features = [ ]
 
 [dependencies.sppark]
-version = "0.1.3"
+version = "0.1.5"
 
 [build-dependencies.cc]
 version = "^1.0.83"
```

### algorithms/cuda/cuda/snarkvm.cu
```diff
@@ -272,7 +272,7 @@ public:
                 RustError ret;
                 try {
                     msm_t<bucket_t, point_t, affine_t, scalar_t> msm(dev);
-                    ret = msm.invoke(partial_sums[i], vec_t<affine_t>{pts, sz},
+                    ret = msm.invoke(partial_sums[i], slice_t<affine_t>{pts, sz},
                                      &scalars[start], false, ffi_affine_size);
                 } catch (const cuda_error& e) {
                     out->inf();
```

### algorithms/src/crypto_hash/poseidon.rs
```diff
@@ -111,6 +111,8 @@ pub struct PoseidonSponge<F: PrimeField, const RATE: usize, const CAPACITY: usiz
     state: State<F, RATE, CAPACITY>,
     /// Current mode (whether its absorbing or squeezing)
     pub mode: DuplexSpongeMode,
+    /// A persistent lookup table used when compressing elements.
+    adjustment_factor_lookup_table: Arc<[F]>,
 }
 
 impl<F: PrimeField, const RATE: usize> AlgebraicSponge<F, RATE> for PoseidonSponge<F, RATE, 1> {
@@ -125,6 +127,18 @@ impl<F: PrimeField, const RATE: usize> AlgebraicSponge<F, RATE> for PoseidonSpon
             parameters: parameters.clone(),
             state: State::default(),
             mode: DuplexSpongeMode::Absorbing { next_absorb_index: 0 },
+            adjustment_factor_lookup_table: {
+                let capacity = F::size_in_bits() - 1;
+                let mut table = Vec::<F>::new();
+
+                let mut cur = F::one();
+                for _ in 0..capacity {
+                    table.push(cur);
+                    cur.double_in_place();
+                }
+
+                table.into()
+            },
         }
     }
 
@@ -318,24 +332,12 @@ impl<F: PrimeField, const RATE: usize> PoseidonSponge<F, RATE, 1> {
 
     /// Compress every two elements if possible.
     /// Provides a vector of (limb, num_of_additions), both of which are F.
-    pub fn compress_elements<TargetField: PrimeField>(src_limbs: &[(F, F)], ty: OptimizationType) -> Vec<F> {
+    pub fn compress_elements<TargetField: PrimeField>(&self, src_limbs: &[(F, F)], ty: OptimizationType) -> Vec<F> {
         let capacity = F::size_in_bits() - 1;
         let mut dest_limbs = Vec::<F>::new();
 
         let params = get_params(TargetField::size_in_bits(), F::size_in_bits(), ty);
 
-        let adjustment_factor_lookup_table = {
-            let mut table = Vec::<F>::new();
-
-            let mut cur = F::one();
-            for _ in 1..=capacity {
-                table.push(cur);
-                cur.double_in_place();
-            }
-
-            table
-        };
-
         let mut i = 0;
         let src_len = src_limbs.len();
         while i < src_len {
@@ -351,7 +353,7 @@ impl<F: PrimeField, const RATE: usize> PoseidonSponge<F, RATE, 1> {
 
             if let Some(second) = second {
                 if first_max_bits_per_limb + second_max_bits_per_limb <= capacity {
-                    let adjustment_factor = &adjustment_factor_lookup_table[second_max_bits_per_limb];
+                    let adjustment_factor = &self.adjustment_factor_lookup_table[second_max_bits_per_limb];
 
                     dest_limbs.push(first.0 * adjustment_factor + second.0);
                     i += 2;
@@ -418,7 +420,7 @@ impl<F: PrimeField, const RATE: usize> PoseidonSponge<F, RATE, 1> {
             }
         }
 
-        let dest_limbs = Self::compress_elements::<TargetField>(&src_limbs, ty);
+        let dest_limbs = self.compress_elements::<TargetField>(&src_limbs, ty);
         self.absorb_native_field_elements(&dest_limbs);
     }
 
```
