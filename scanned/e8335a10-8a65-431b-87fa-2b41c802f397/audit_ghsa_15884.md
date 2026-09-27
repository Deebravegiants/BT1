# [M] Databento Binary Encoding (DBN) has a heap buffer overflow using c_chars_to_str function

## Summary
Severity: Medium
Advisory: GHSA-pfr9-2p92-qrhq
CWE: CWE-126
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-09
Source: https://github.com/advisories/GHSA-pfr9-2p92-qrhq
Type: github-advisory

## Affected
- crates.io: `dbn` — affected >=0 <0.22.1

## Details
The `heap-buffer-overflow` is triggered in the `strlen()` function when handling the `c_chars_to_str` function in the dbn crate. This vulnerability occurs because the `CStr::from_ptr()` function in Rust assumes that the provided C string is null-terminated. However, there is no guarantee that the input chars array passed to the c_chars_to_str function is properly null-terminated.

If the chars array does not contain a null byte (\0), strlen() will continue to read beyond the bounds of the buffer in search of a null terminator. This results in an out-of-bounds memory read and can lead to a heap-buffer-overflow, potentially causing memory corruption or exposing sensitive information.

## References
- https://github.com/databento/dbn/issues/67
- https://github.com/databento/dbn/commit/339efb90fdb980920a5e8829008abc1114f4bfdd
- https://github.com/databento/dbn
- https://rustsec.org/advisories/RUSTSEC-2024-0377.html
