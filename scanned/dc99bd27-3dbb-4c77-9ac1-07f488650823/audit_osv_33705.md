# [C] NeKernel has Heap Overflow in `rt_copy_memory`

## Summary
Severity: Critical
Advisory: CVE-2025-48990
Aliases: GHSA-jvvh-fp57-2p32
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-06-02
Source: https://osv.dev/vulnerability/CVE-2025-48990
Type: osv

## Details
NeKernal is a free and open-source operating system stack. Version 0.0.2 has a 1-byte heap overflow in `rt_copy_memory`, which unconditionally wrote a null terminator at `dst[len]`. When `len` equals the size of the destination buffer (256 bytes), that extra `'\0'` write overruns the buffer by one byte. To avoid breaking existing callers or changing the public API, the patch in commit fb7b7f658327f659c6a6da1af151cb389c2ca4ee takes a minimal approach: it simply removes the overflow-causing line without adding bounds checks or altering the function signature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48990.json
- https://github.com/nekernel-org/nekernel/security/advisories/GHSA-jvvh-fp57-2p32
- https://nvd.nist.gov/vuln/detail/CVE-2025-48990
- https://github.com/nekernel-org/nekernel/commit/fb7b7f658327f659c6a6da1af151cb389c2ca4ee
