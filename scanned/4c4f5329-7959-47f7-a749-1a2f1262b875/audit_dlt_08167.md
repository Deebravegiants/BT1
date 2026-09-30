# [?] fix(deps): update h2 to 0.4.16 for RUSTSEC-2026-0258 and drop the resolved quick-xml ignores

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-18
Source: https://github.com/ZcashFoundation/zebra/commit/8648d0887550115e74458024096bee0420680e23
Type: security-commit

## Details
fix(deps): update h2 to 0.4.16 for RUSTSEC-2026-0258 and drop the resolved quick-xml ignores

## Patch
### Cargo.lock
```diff
@@ -156,7 +156,7 @@ version = "1.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "40c48f72fd53cd289104fc64099abca73db4166ad86ea0b4341abe65af83dadc"
 dependencies = [
- "windows-sys 0.60.2",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -167,7 +167,7 @@ checksum = "291e6a250ff86cd4a820112fb8898808a366d8f9f58ce16d1f538353ad55747d"
 dependencies = [
  "anstyle",
  "once_cell_polyfill",
- "windows-sys 0.60.2",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -1583,7 +1583,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"
 dependencies = [
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -1948,9 +1948,9 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.4.13"
+version = "0.4.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2f44da3a8150a6703ed5d34e164b875fd14c2cdab9af1252a9a1020bde2bdc54"
+checksum = "a9f37a958b41b3b19ee2707c06439c0e9e547e847223eb791ecb0cb821c65e27"
 dependencies = [
  "atomic-waker",
  "bytes",
@@ -2619,7 +2619,7 @@ checksum = "3640c1c38b8e4e43584d8df18be5fc6b0aa314ce6ebf51b53313d4306cca8e46"
 dependencies = [
  "hermit-abi",
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -4205,7 +4205,7 @@ dependencies = [
  "once_cell",
  "socket2",
  "tracing",
- "windows-sys 0.60.2",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -4724,7 +4724,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -4783,7 +4783,7 @@ dependencies = [
  "security-framework",
  "security-framework-sys",
  "webpki-root-certs",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -5347,7 +5347,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3a766e1110788c36f4fa1c2b71b387a7815aa65f88ce0229841826633d93723e"
 dependencies = [
  "libc",
- "windows-sys 0.60.2",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -5545,7 +5545,7 @@ dependencies = [
  "getrandom 0.4.2",
  "once_cell",
  "rustix",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -6727,7 +6727,7 @@ version = "0.1.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c2a7b1c03c876122aa43f3020e6c3c3ee5c05081c9a00739faf7503aeba10d22"
 dependencies = [
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -6801,7 +6801,7 @@ version = "0.52.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "282be5f36a8ce781fad8c8ae18fa3f9beff57ec1b52cb3de0789201425d9a33d"
 dependencies = [
- "windows-targets 0.52.6",
+ "windows-targets",
 ]
 
 [[package]]
@@ -6810,16 +6810,7 @@ version = "0.59.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1e38bc4d79ed67fd075bcc251a1c39b32a1776bbe92e5bef1f0bf1f8c531853b"
 dependencies = [
- "windows-targets 0.52.6",
-]
-
-[[package]]
-name = "windows-sys"
-version = "0.60.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f2f500e4d28234f72040990ec9d39e3a6b950f9f22d3dba18416c35882612bcb"
-dependencies = [
- "windows-targets 0.53.5",
+ "windows-targets",
 ]
 
 [[package]]
@@ -6837,31 +6828,14 @@ version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9b724f72796e036ab90c1021d4780d4d3d648aca59e491e6b98e725b84e99973"
 dependencies = [
- "windows_aarch64_gnullvm 0.52.6",
- "windows_aarch64_msvc 0.52.6",
- "windows_i686_gnu 0.52.6",
- "windows_i686_gnullvm 0.52.6",
- "windows_i686_msvc 0.52.6",
- "windows_x86_64_gnu 0.52.6",
- "windows_x86_64_gnullvm 0.52.6",
- "windows_x86_64_msvc 0.52.6",
-]
-
-[[package]]
-name = "windows-targets"
-version = "0.53.5"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4945f9f551b88e0d65f3db0bc25c33b8acea4d9e41163edf90dcd0b19f9069f3"
-dependencies = [
- "windows-link",
- "windows_aarch64_gnullvm 0.53.1",
- "windows_aarch64_msvc 0.53.1",
- "windows_i686_gnu 0.53.1",
- "windows_i686_gnullvm 0.53.1",
- "windows_i686_msvc 0.53.1",
- "windows_x86_64_gnu 0.53.1",
- "windows_x86_64_gnullvm 0.53.1",
- "windows_x86_64_msvc 0.53.1",
+ "windows_aarch64_gnullvm",
+ "windows_aarch64_msvc",
+ "windows_i686_gnu",
+ "windows_i686_gnullvm",
+ "windows_i686_msvc",
+ "windows_x86_64_gnu",
+ "windows_x86_64_gnullvm",
+ "windows_x86_64_msvc",
 ]
 
 [[package]]
@@ -6870,96 +6844,48 @@ version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "32a4622180e7a0ec044bb555404c800bc9fd9ec262ec147edd5989ccd0c02cd3"
 
-[[package]]
-name = "windows_aarch64_gnullvm"
-version = "0.53.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a9d8416fa8b42f5c947f8482c43e7d89e73a173cead56d044f6a56104a6d1b53"
-
 [[package]]
 name = "windows_aarch64_msvc"
 version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "09ec2a7bb152e2252b53fa7803150007879548bc709c039df7627cabbd05d469"
 
-[[package]]
-name = "windows_aarch64_msvc"
-version = "0.53.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b9d782e804c2f632e395708e99a94275910eb9100b2114651e04744e9b125006"
-
 [[package]]
 name = "windows_i686_gnu"
 version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8e9b5ad5ab802e97eb8e295ac6720e509ee4c243f69d781394014ebfe8bbfa0b"
 
-[[package]]
-name = "windows_i686_gnu"
-version = "0.53.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "960e6da069d81e09becb0ca57a65220ddff016ff2d6af6a223cf372a506593a3"
-
 [[package]]
 name = "windows_i686_gnullvm"
 version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0eee52d38c090b3caa76c563b86c3a4bd71ef1a819287c19d586d7334ae8ed66"
 
-[[package]]
-name = "windows_i686_gnullvm"
-version = "0.53.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fa7359d10048f68ab8b09fa71c3daccfb0e9b559aed648a8f95469c27057180c"
-
 [[package]]
 name = "windows_i686_msvc"
 version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "240948bc05c5e7c6dabba28bf89d89ffce3e303022809e73deaefe4f6ec56c66"
 
-[[package]]
-name = "windows_i686_msvc"
-version = "0.53.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1e7ac75179f18232fe9c285163565a57ef8d3c89254a30685b57d83a38d326c2"
-
 [[package]]
 name = "windows_x86_64_gnu"
 version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "147a5c80aabfbf0c7d901cb5895d1de30ef2907eb21fbbab29ca94c5b08b1a78"
 
-[[package]]
-name = "windows_x86_64_gnu"
-version = "0.53.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9c3842cdd74a865a8066ab39c8a7a473c0778a3f29370b5fd6b4b9aa7df4a499"
-
 [[package]]
 name = "windows_x86_64_gnullvm"
 version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "24d5b23dc417412679681396f2b49f3de8c1473deb516bd34410872eff51ed0d"
 
-[[package]]
-name = "windows_x86_64_gnullvm"
-version = "0.53.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0ffa179e2d07eee8ad8f57493436566c7cc30ac536a3379fdf008f47f6bb7ae1"
-
 [[package]]
 name = "windows_x86_64_msvc"
 version = "0.52.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "589f6da84c646204747d1270a2a5661ea66ed1cced2631d546fdfb155959f9ec"
 
-[[package]]
-name = "windows_x86_64_msvc"
-version = "0.53.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d6bbff5f0aada427a1e5a6da5f1f98158182f26556f345ac9e04d36d0ebed650"
-
 [[package]]
 name = "winnow"
 version = "1.0.2"
```

### deny.toml
```diff
@@ -15,11 +15,6 @@ ignore = [
     "RUSTSEC-2026-0173", # proc-macro-error2 (unmaintained): via librustzcash orchard -> getset
     "RUSTSEC-2025-0119", # number_prefix: transitive via indicatif
     "RUSTSEC-2025-0141", # bincode: direct dependency
-    # quick-xml DoS advisories: via inferno (zebrad's `flamegraph` feature), which has no release
-    # allowing the fixed quick-xml 0.41 yet: https://github.com/jonhoo/inferno/pull/369.
-    # Zebra only feeds inferno locally generated profiling data, never untrusted XML.
-    "RUSTSEC-2026-0194", # quick-xml: quadratic duplicate-attribute check
-    "RUSTSEC-2026-0195", # quick-xml: unbounded namespace-declaration allocation
 ]
 
 # This section is considered when running `cargo deny check licenses`.
```
