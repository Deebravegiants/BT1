# [?] Handle quick-xml RUSTSEC-2026-0194/0195: drop unused pprof flamegraph feature, ignore rest

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-02
Source: https://github.com/Conflux-Chain/conflux-rust/commit/4b7cf28dab840a181292f86ba473a7a1a0a0a33a
Type: security-commit

## Details
Handle quick-xml RUSTSEC-2026-0194/0195: drop unused pprof flamegraph feature, ignore rest

quick-xml's DoS fixes ship only in 0.41.0 and no inferno release depends on it yet, so no upgrade path exists today.

pprof's "flamegraph" feature was never used (CPU profiles are served as protobuf only), so dropping it removes the inferno 0.11 -> quick-xml 0.26 subtree outright.

The remaining quick-xml 0.37 comes from jemalloc_pprof's heap-flamegraph SVG endpoint, which only writes SVG and never parses untrusted XML, so the advisories are ignored with justification in deny.toml and .cargo/audit.toml until inferno adopts quick-xml >= 0.41.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

## Patch
### .cargo/audit.toml
```diff
@@ -1,4 +1,11 @@
 [advisories]
 ignore = [
     "RUSTSEC-2025-0055", # tracing-subscriber 0.2.25 Introduced by `revm`.
+    # quick-xml DoS advisories, patched only in >= 0.41.0; pulled via
+    # jemalloc_pprof -> inferno, whose APIs used here only write
+    # flamegraph SVG (no untrusted-XML parsing reachable). No inferno
+    # release uses quick-xml 0.41 yet. See deny.toml for details; drop
+    # when upstream catches up.
+    "RUSTSEC-2026-0194",
+    "RUSTSEC-2026-0195",
 ]
```

### Cargo.lock
```diff
@@ -4846,24 +4846,6 @@ dependencies = [
  "serde",
 ]
 
-[[package]]
-name = "inferno"
-version = "0.11.21"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "232929e1d75fe899576a3d5c7416ad0d88dbfbb3c3d6aa00873a7408a50ddb88"
-dependencies = [
- "ahash 0.8.11",
- "indexmap 2.8.0",
- "is-terminal",
- "itoa",
- "log",
- "num-format",
- "once_cell",
- "quick-xml 0.26.0",
- "rgb",
- "str_stack",
-]
-
 [[package]]
 name = "inferno"
 version = "0.12.3"
@@ -4881,7 +4863,7 @@ dependencies = [
  "log",
  "num-format",
  "once_cell",
- "quick-xml 0.37.5",
+ "quick-xml",
  "rgb",
  "str_stack",
 ]
@@ -4956,17 +4938,6 @@ dependencies = [
  "serde",
 ]
 
-[[package]]
-name = "is-terminal"
-version = "0.4.17"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3640c1c38b8e4e43584d8df18be5fc6b0aa314ce6ebf51b53313d4306cca8e46"
-dependencies = [
- "hermit-abi",
- "libc",
- "windows-sys 0.61.2",
-]
-
 [[package]]
 name = "is_terminal_polyfill"
 version = "1.70.1"
@@ -6674,7 +6645,6 @@ dependencies = [
  "backtrace",
  "cfg-if 1.0.0",
  "findshlibs",
- "inferno 0.11.21",
  "libc",
  "log",
  "nix",
@@ -6697,7 +6667,7 @@ dependencies = [
  "anyhow",
  "backtrace",
  "flate2",
- "inferno 0.12.3",
+ "inferno",
  "num",
  "paste",
  "prost",
@@ -6986,15 +6956,6 @@ version = "1.2.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a1d01941d82fa2ab50be1e79e6714289dd7cde78eba4c074bc5a4374f650dfe0"
 
-[[package]]
-name = "quick-xml"
-version = "0.26.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7f50b1c63b38611e7d4d7f68b82d3ad0cc71a2ad2e7f61fc10f1328d917c93cd"
-dependencies = [
- "memchr",
-]
-
 [[package]]
 name = "quick-xml"
 version = "0.37.5"
```

### Cargo.toml
```diff
@@ -296,8 +296,10 @@ tikv-jemallocator = { version = "0.6", features = ["profiling", "unprefixed_mall
 # tikv-jemalloc-ctl = { version = "0.6", features = ["use_std", "stats"] }
 # tikv-jemalloc-sys = { version = "0.6", features = ["profiling"] }
 jemalloc_pprof = { version = "0.8", features = ["symbolize", "flamegraph"] }
-# CPU profiling
-pprof = { version = "0.15", features = ["flamegraph", "protobuf-codec"] }
+# CPU profiling. No "flamegraph" feature: CPU profiles are served as pprof
+# protobuf only, and the feature would pull inferno -> quick-xml
+# (RustSec-flagged, see deny.toml).
+pprof = { version = "0.15", features = ["protobuf-codec"] }
 tracy-client = "0.18.0"
 snmalloc-rs = { version = "0.3.7", features = ["build_cc"] }
 
```

### deny.toml
```diff
@@ -94,6 +94,21 @@ ignore = [
     { id = "RUSTSEC-2026-0097", reason = "rand 0.9 patched; 0.7/0.8 forced by transitive deps and upstream pins; vulnerable code path not reachable here." },
     # proc-macro-error2 is unmaintained; pulled by alloy-sol-macro 1.6.0
     "RUSTSEC-2026-0173",
+    # quick-xml DoS advisories (quadratic duplicate-attribute check;
+    # unbounded NsReader namespace allocation), patched only in
+    # quick-xml >= 0.41.0. Pulled transitively for the heap-flamegraph
+    # SVG endpoint: jemalloc_pprof -> pprof_util -> inferno 0.12
+    # (quick-xml 0.37); pprof's unused "flamegraph" feature is disabled
+    # in Cargo.toml so the CPU-profiling path pulls no quick-xml. No
+    # inferno release depends on quick-xml 0.41 yet (latest 0.12.6 pins
+    # ^0.39), so no upgrade path exists. The vulnerable paths parse
+    # untrusted XML; the inferno APIs used here only *write* flamegraph
+    # SVG (its from_reader inputs are folded stack text; inferno's sole
+    # XML reader, collapse/xctrace, is never called), so they are
+    # unreachable. Drop these once inferno updates to quick-xml >= 0.41
+    # and jemalloc_pprof picks it up.
+    { id = "RUSTSEC-2026-0194", reason = "quick-xml used write-only via inferno flamegraph output; no patched upstream chain yet." },
+    { id = "RUSTSEC-2026-0195", reason = "NsReader not used by inferno; quick-xml write-only here; no patched upstream chain yet." },
 ]
 # If this is true, then cargo deny will use the git executable to fetch advisory database.
 # If this is false, then it uses a built-in git library.
```
