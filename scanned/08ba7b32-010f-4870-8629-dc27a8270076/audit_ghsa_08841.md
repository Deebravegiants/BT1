# [H] gix-pack has multiple DoS vectors: unchecked indexing panics and uncapped OOM allocations from crafted pack data

## Summary
Severity: High
Advisory: GHSA-x494-mj8g-cj27
CWE: CWE-248, CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-x494-mj8g-cj27
Type: github-advisory

## Affected
- crates.io: `gix-pack` — affected >=0 <0.69.0

## Details
### Summary

Multiple denial-of-service vectors in `gix-pack`: unchecked array indexing causes panics on crafted delta data, and uncapped attacker-controlled size headers enable OOM process kills. Both are triggered by malicious pack data received during clone/fetch.

### Details

**Bug 1: Unchecked array indexing in delta application (CWE-248)**

The `apply()` function in `gix-pack/src/data/delta.rs` (lines 33-87) reads delta instructions using unchecked `data[i]` indexing at 7 locations (lines 41, 45, 49, 53, 57, 61, 65). The command byte's bits indicate how many additional bytes follow, but if the delta data is truncated, the index panics:

```rust
pub(crate) fn apply(base: &[u8], mut target: &mut [u8], data: &[u8]) -> Result<(), apply::Error> {
    let mut i = 0;
    while let Some(cmd) = data.get(i) {  // first byte: safely checked
        i += 1;
        match cmd {
            cmd if cmd & 0b1000_0000 != 0 => {
                let (mut ofs, mut size): (u32, u32) = (0, 0);
                if cmd & 0b0000_0001 != 0 {
                    ofs = u32::from(data[i]);     // PANIC: no bounds check
                    i += 1;
                }
                // ... 6 more unchecked data[i] at lines 45, 49, 53, 57, 61, 65
```

Lines 83-84 use `assert_eq!` (not `debug_assert_eq!`) that panics in both debug and release builds:

```rust
    assert_eq!(i, data.len());
    assert_eq!(target.len(), 0);
```

A second location in `parse_header_info()` (`gix-pack/src/data/entry/decode.rs:116-129`) also panics on truncated input via unchecked `data[0]` and `data[i]`.

Note: PR #2059 (merged 2025-06-25) fixed the explicit `panic!()` for command code 0. The unchecked array indexing is a distinct class that remains unfixed.

**Bug 2: Uncapped allocation from attacker-controlled size headers (CWE-770)**

Pack entry headers and delta headers encode object sizes as LEB128-encoded u64 values. These sizes are used to allocate buffers before validating the actual data, with no upper bound:

```
bytes_to_entries.rs:109  Vec::with_capacity(entry.decompressed_size as usize)  // UNCAPPED
resolve.rs:461           out.resize(decompressed_len, 0)                       // UNCAPPED
resolve.rs:190           fully_resolved_delta_bytes.resize(result_size as usize, 0)  // UNCAPPED
```

A 10-byte crafted pack entry can claim `decompressed_size = 0xFFFFFFFFFFFF` (281 TB). At `bytes_to_entries.rs:109`, gitoxide calls `Vec::with_capacity(281TB)` **before any decompression occurs**. The OS immediately OOM-kills the process. No `MAX_SIZE`, `max_object_size`, or equivalent limit exists anywhere in gix-pack.

The allocation at `resolve.rs:461` is equally dangerous: `decompressed_size` from the pack header is cast to `usize` and passed to `Vec::resize()`, which allocates and zeroes the full claimed size before the zlib decompressor runs.

### PoC

Compiled and executed in Rust 1.94.1 `--release` mode. All 5 panics confirmed:

```
[1] delta apply: cmd=0x81, truncated -> PANIC: index out of bounds: len is 1 but index is 1
[2] delta apply: cmd=0xFF, only 3 extra bytes -> PANIC: index out of bounds: len is 4 but index is 4
[3] parse_header_info: empty data -> PANIC: index out of bounds: len is 0 but index is 0
[4] parse_header_info: byte=0x80, truncated -> PANIC: index out of bounds: len is 1 but index is 1
[5] delta apply: assert_eq!(i, data.len()) -> PANIC: assertion failed
```

For the OOM vector: the allocation path is `parse_header_info()` -> `entry.decompressed_size` (u64) -> `Vec::with_capacity(size as usize)` with no intermediate validation. A minimal pack with a single entry claiming a multi-terabyte size triggers immediate process kill.

### Impact

Any application built on gitoxide that clones or fetches from an untrusted remote can be crashed by a malicious server:

- **Panic DoS**: 1-2 bytes of crafted delta data causes an immediate process abort
- **OOM DoS**: A single crafted pack entry header causes the process to attempt a multi-terabyte allocation, triggering an immediate OOM kill by the OS

This affects the `gix` CLI, any application using the `gix` crate, and CI/CD systems that clone repositories using gitoxide. No fuzz targets exist for gix-pack (issue #703 tracks oss-fuzz integration).

### Suggested fix

For panics: replace unchecked `data[i]` with `data.get(i).ok_or(Error::...)` and replace `assert_eq!` with proper error returns.

For OOM: add a configurable maximum object size (similar to git's `transfer.maxPackSize`) and validate claimed sizes against it before allocating. At minimum, cap allocations to a reasonable default (e.g., 4 GB) and use `try_reserve()` consistently.

### Severity

High. Network vector, no privileges required, user interaction required (clone/fetch). The OOM vector is a single-packet process kill with no recovery.

## References
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-x494-mj8g-cj27
- https://github.com/GitoxideLabs/gitoxide
