# [M] OpenEXR has a signed integer overflow (undefined behavior) in undo_pxr24_impl may allow bounds-check bypass in PXR24 decompression

## Summary
Severity: Medium
Advisory: CVE-2026-34380
Aliases: GHSA-q3v8-hw4m-59w5
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-34380
Type: osv

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From 3.2.0 to before 3.2.7, 3.3.9, and 3.4.9, a signed integer overflow exists in undo_pxr24_impl() in src/lib/OpenEXRCore/internal_pxr24.c at line 377. The expression (uint64_t)(w * 3) computes w * 3 as a signed 32-bit integer before casting to uint64_t. When w is large, this multiplication constitutes undefined behavior under the C standard. On tested builds (clang/gcc without sanitizers), two's-complement wraparound commonly occurs, and for specific values of w the wrapped result is a small positive integer, which may allow the subsequent bounds check to pass incorrectly. If the check is bypassed, the decoding loop proceeds to write pixel data through dout, potentially extending far beyond the allocated output buffer. This vulnerability is fixed in 3.2.7, 3.3.9, and 3.4.9.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.2.7
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.9
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.9
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-q3v8-hw4m-59w5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34380.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34380
