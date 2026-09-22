# [M] A heap-based buffer over-read or buffer overflow in davisking/dlib

## Summary
Severity: Medium
Advisory: CVE-2026-24799
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:A/VC:N/VI:L/VA:H/SC:N/SI:L/SA:L/S:N/AU:Y/R:U/V:C/RE:L/U:Amber)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24799
Type: osv

## Details
Out-of-bounds Write, Buffer Copy without Checking Size of Input ('Classic Buffer Overflow') vulnerability in davisking dlib (dlib/external/zlib modules). This vulnerability is associated with program files inflate.C.

This issue affects dlib: before v19.24.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24799.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24799
- https://github.com/davisking/dlib/pull/3063
- https://github.com/davisking/dlib
