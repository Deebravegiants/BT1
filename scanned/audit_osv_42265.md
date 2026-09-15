# [C] libssh2 Heap Out-of-Bounds Read via publickey subsystem

## Summary
Severity: Critical
Advisory: CVE-2026-66034
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66034
Type: osv

## Details
libssh2 through 1.11.1, fixed in commit a13bb6c, contains a missing bounds check vulnerability that allows a malicious SSH server to trigger an arbitrary-length heap out-of-bounds read and a free of an uninitialized pointer via the publickey subsystem. In libssh2_publickey_list_fetch(), the version 1 response parser reads a server-controlled comment_len value and advances the parse pointer without verifying sufficient bytes remain in the buffer, causing the out-of-bounds read to leak heap pointers from adjacent allocations defeating ASLR, followed by heap allocator state corruption when the error cleanup path frees an uninitialized pointer from a non-zeroed realloc() region.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66034.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66034
- https://www.vulncheck.com/advisories/libssh2-heap-out-of-bounds-read-via-publickey-subsystem
- https://github.com/libssh2/libssh2/commit/a13bb6c773f0d55ad1628cede57e99803cd898d9
- https://github.com/libssh2/libssh2/pull/2202
- https://github.com/libssh2/libssh2
