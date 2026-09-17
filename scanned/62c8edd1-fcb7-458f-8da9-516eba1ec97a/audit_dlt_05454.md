# [?] fix: update bytes from 1.10.1 to 1.11.1 (RUSTSEC-2026-0007) (#5099)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-02-04
Source: https://github.com/nervosnetwork/ckb/commit/696455dc5000f7bf077e208f4d56c9e452785d84
Type: security-commit

## Details
fix: update bytes from 1.10.1 to 1.11.1 (RUSTSEC-2026-0007) (#5099)

### What problem does this PR solve?

Problem Summary:

RUSTSEC-2026-0007: Integer overflow in `BytesMut::reserve` allows
unchecked addition of `new_cap + offset` to wrap in release builds,
corrupting capacity tracking and enabling out-of-bounds memory access.

### What is changed and how it works?

What's Changed:

- Bump `bytes` dependency from `1.10.1` to `1.11.1` in workspace
`Cargo.toml`
- Update `Cargo.lock` to reflect patched version

Version 1.11.1 adds overflow checks to the reserve path, preventing
capacity corruption.

### Related changes

- N/A

### Check List

Tests

- No code

Side effects

- N/A

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>RUSTSEC-2026-0007: Integer overflow in
`BytesMut::reserve`</issue_title>
> <issue_description>
> > Integer overflow in `BytesMut::reserve`
> 
> | Details | |
> | ------------------- | ----------------------------------------------
|
> | Package             | `bytes`                      |
> | Version             | `1.10.1`                   |
> | URL |
[https://github.com/advisories/GHSA-434x-w66g-qw3r](https://github.com/advisories/GHSA-434x-w66g-qw3r)
|
> | Date                | 2026-02-03                         |
> | Patched versions    | `>=1.11.1`                  |
> | Unaffected versions | `<1.2.1`               |
> 
> In the unique reclaim path of `BytesMut::reserve`, the condition
> ```rs
> if v_capacity &gt;= new_cap + offset
> ```
> uses an unchecked addition. When `new_cap + offset` overflows `usize`
in release builds, this condition may incorrectly pass, causing
`self.cap` to be set to a value that exceeds the actual allocated
capacity. Subsequent APIs such as `spare_capacity_mut()` then trust this
corrupted `cap` value and may create out-of-bounds slices, leading to
UB.
> 
> This behavior is observable in release builds (integer overflow
wraps), whereas debug builds panic due to overflow checks.
> 
> ## PoC
> 
> ```rs
> use bytes::*;
> 
> fn main() {
>     let mut a = BytesMut::from(&amp;b&quot;hello world&quot;[..]);
>     let mut b = a.split_off(5);
> 
>     // Ensure b becomes the unique owner of the backing storage
>     drop(a);
> 
>     // Trigger overflow in new_cap + offset inside reserve
>     b.reserve(usize::MAX - 6);
> 
> // This call relies on the corrupted cap and may cause UB &amp; HBO
>     b.put_u8(b&#39;h&#39;);
> }
> ```
> 
> # Workarounds
> 
> Users of `BytesMut::reserve` are only affected if integer overflow
checks are configured to wrap. When integer overflow is configured to
panic, this issue does not apply.
> 
> See [advisory
page](https://rustsec.org/advisories/RUSTSEC-2026-0007.html) for
additional details.
> </issue_description>
> 
> ## Comments on the Issue (you are @copilot in this section)
> 
> <comments>
> </comments>
> 


</details>



<!-- START COPILOT CODING AGENT SUFFIX -->

- Fixes nervosnetwork/ckb#5098

<!-- START COPILOT CODING AGENT TIPS -->
---

💬 We'd love your input! Share your thoughts on Copilot coding agent in
our [2 minute survey](https://gh.io/copilot-coding-agent-survey).

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: eval-exec <46400566+eval-exec@users.noreply.github.com>

### Cargo.lock
```diff
@@ -545,9 +545,9 @@ checksum = "1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b"
 
 [[package]]
 name = "bytes"
-version = "1.10.1"
+version = "1.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d71b6127be86fdcfddb610f7182ac57211d4b18a3e9c82eb2d17662f2227ad6a"
+checksum = "1e748733b7cbc798e1434b6ac524f0c1ff2ab456fe201501e6497c8417a4fc33"
 dependencies = [
  "serde",
 ]
@@ -1355,7 +1355,7 @@ dependencies = [
  "ckb-pow",
  "ckb-stop-handler",
  "ckb-types",
- "console 0.15.11",
+ "console",
  "eaglesong",
  "futures",
  "http-body-util",
@@ -2143,19 +2143,6 @@ dependencies = [
  "crossbeam-utils",
 ]
 
-[[package]]
-name = "console"
-version = "0.15.11"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "054ccb5b10f9f2cbf51eb355ca1d05c2d279ce1804688d0db74b4733a5aeafd8"
-dependencies = [
- "encode_unicode",
- "libc",
- "once_cell",
- "unicode-width 0.2.2",
- "windows-sys 0.59.0",
-]
-
 [[package]]
 name = "console"
 version = "0.16.1"
@@ -2784,7 +2771,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"
 dependencies = [
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -3880,7 +3867,7 @@ version = "0.18.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9375e112e4b463ec1b1c6c011953545c65a30164fbab5b581df32b3abf0dcb88"
 dependencies = [
- "console 0.16.1",
+ "console",
  "portable-atomic",
  "rayon",
  "unicode-width 0.2.2",
@@ -3951,7 +3938,7 @@ checksum = "3640c1c38b8e4e43584d8df18be5fc6b0aa314ce6ebf51b53313d4306cca8e46"
 dependencies = [
  "hermit-abi",
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -5651,7 +5638,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.11.0",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -6603,7 +6590,7 @@ dependencies = [
  "getrandom 0.3.4",
  "once_cell",
  "rustix 1.1.2",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -7658,7 +7645,7 @@ version = "0.1.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c2a7b1c03c876122aa43f3020e6c3c3ee5c05081c9a00739faf7503aeba10d22"
 dependencies = [
- "windows-sys 0.48.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
```

### Cargo.toml
```diff
@@ -137,7 +137,7 @@ blake2b-ref = "0.3"
 bloom-filters = "0.1"
 bs58 = "0.5.0"
 byteorder = "1.3.1"
-bytes = "1"
+bytes = "1.11.1"
 cfg-if = "1.0"
 ckb-app-config = { path = "util/app-config", version = "1" }
 ckb-async-runtime = { path = "util/runtime", version = "1" }
```
