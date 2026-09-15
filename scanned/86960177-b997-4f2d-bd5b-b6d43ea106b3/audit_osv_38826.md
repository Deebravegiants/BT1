# [M] CVE-2026-42476

## Summary
Severity: Medium
Advisory: CVE-2026-42476
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-42476
Type: osv

## Details
Two heap-based out-of-bounds read vulnerabilities in the STL ASCII file parser in Open CASCADE Technology (OCCT) V8_0_0_rc5 exist in RWStl_Reader::ReadAscii because buffers returned by Standard_ReadLineBuffer::ReadLine() are not properly length-validated before strncasecmp or direct byte access. User-assisted attackers can trigger these issues by persuading a victim to open a crafted STL file with extremely short lines, resulting in a denial of service or possible information disclosure.

## References
- https://gist.github.com/sgInnora/dfba083d04906283e9c92aea78e2d94a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42476.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42476
