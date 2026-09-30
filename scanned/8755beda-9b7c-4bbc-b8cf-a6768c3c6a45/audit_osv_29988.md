# [H] CVE-2024-48615

## Summary
Severity: High
Advisory: CVE-2024-48615
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-28
Source: https://osv.dev/vulnerability/CVE-2024-48615
Type: osv

## Details
Null Pointer Dereference vulnerability in libarchive 3.7.6 and earlier when running program bsdtar in function header_pax_extension at rchive_read_support_format_tar.c:1844:8.

## References
- https://github.com/libarchive/libarchive/releases/download/v3.7.6/libarchive-3.7.6.tar.gz
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48615.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48615
- https://github.com/88Sanghy88/crash-test
