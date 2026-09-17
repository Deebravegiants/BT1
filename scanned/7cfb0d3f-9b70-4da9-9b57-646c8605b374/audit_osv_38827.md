# [M] CVE-2026-42477

## Summary
Severity: Medium
Advisory: CVE-2026-42477
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-42477
Type: osv

## Details
A heap-based out-of-bounds read vulnerability in RWObj_Reader::read in the OBJ file parser in Open CASCADE Technology (OCCT) V8_0_0_rc5 allows user-assisted attackers to cause a denial of service or obtain sensitive information by persuading a victim to open a crafted OBJ file. The issue occurs because Standard_ReadLineBuffer::ReadLine() can return a 1-byte buffer for a minimal OBJ line, and RWObj_Reader::read() calls pushIndices(aLine + 2) without validating the buffer length.

## References
- https://gist.github.com/sgInnora/dfba083d04906283e9c92aea78e2d94a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42477.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42477
