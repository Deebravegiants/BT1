# [C] libssh2 through 1.11.1, fixed in commit a13bb6c, contains a missing bounds check vulnerability...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1087
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/JLSEC-2026-1087
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.11.104+0

## Details
libssh2 through 1.11.1, fixed in commit a13bb6c, contains a missing bounds check vulnerability that allows a malicious SSH server to trigger an arbitrary-length heap out-of-bounds read and a free of an uninitialized pointer via the publickey subsystem. In `libssh2_publickey_list_fetch()`, the version 1 response parser reads a server-controlled `comment_len` value and advances the parse pointer without verifying sufficient bytes remain in the buffer, causing the out-of-bounds read to leak heap pointers from adjacent allocations defeating ASLR, followed by heap allocator state corruption when the error cleanup path frees an uninitialized pointer from a non-zeroed realloc() region.

## References
- https://github.com/advisories/GHSA-6h6q-9mwg-r6x7
- https://github.com/libssh2/libssh2/commit/a13bb6c773f0d55ad1628cede57e99803cd898d9
- https://github.com/libssh2/libssh2/pull/2202
- https://nvd.nist.gov/vuln/detail/CVE-2026-66034
- https://www.vulncheck.com/advisories/libssh2-heap-out-of-bounds-read-via-publickey-subsystem
