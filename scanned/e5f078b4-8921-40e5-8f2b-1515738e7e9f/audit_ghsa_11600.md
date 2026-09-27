# [H] lz4_flex's decompression can leak information from uninitialized memory or reused output buffer

## Summary
Severity: High
Advisory: GHSA-vvp9-7p8x-rfvv
CVE: CVE-2026-32829
CWE: CWE-201, CWE-823
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-vvp9-7p8x-rfvv
Type: github-advisory

## Affected
- crates.io: `lz4_flex` — affected >=0 <0.11.6
- crates.io: `lz4_flex` — affected >=0.12.0 <0.12.1

## Details
### Summary
Decompressing invalid LZ4 data can leak data from uninitialized memory, or can leak content from previous decompression operations when reusing an output buffer.

### Details
The LZ4 block format defines a "match copy operation" which duplicates previously written data or data from the user-supplied dict. The position of that data is defined by an _offset_. The data is copied within the output buffer from the _offset_ to the current output position.
However, lz4_flex did not properly detect invalid and out-of-bounds _offset_ values properly, causing it to copy uninitialized data from the output buffer.

Only the block based API functions are affected: 
`lz4_flex::block::{decompress_into, decompress_into_with_dict}`

When safe-decode is disabled _additionally_ these functions are affected
`lz4_flex::block::{decompress, decompress_with_dict, decompress_size_prepended, decompress_size_prepended_with_dict}`

All `frame` APIs are _not_ affected.

There are two affected use cases:
- decompressing LZ4 data with the `unsafe` implementation (`safe-decode` feature flag disabled, which is enabled by default):
can leak content of uninitialized memory as decompressed result
- decompressing LZ4 data into a reused, user-supplied `output` buffer (affects the `safe-decode` feature as well):
can leak the previous contents of the output buffer as decompressed result

### Impact
Leakage of data from uninitialized memory or content from previous decompression operations, possibly revealing sensitive information and secrets.

### Mitigation
lz4_flex 0.12.1 and 0.11.6 fixes this issue without requiring changes in user code.

If you cannot upgrade, you can mitigate this vulnerability by zeroing the output buffer before calling `block::decompress_into` or  `block::decompress_into_with_dict` (only block based API is affected, frame API is not affected). Additionally the the `safe-decode` feature flag should be enabled.

## References
- https://github.com/PSeitz/lz4_flex/security/advisories/GHSA-vvp9-7p8x-rfvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-32829
- https://github.com/PSeitz/lz4_flex/commit/055502ee5d297ecd6bf448ac91c055c7f6df9b6d
- https://github.com/PSeitz/lz4_flex
- https://rustsec.org/advisories/RUSTSEC-2026-0041.html
