# [M] OpenSIPS: OOB Read in Multipart Body Boundary Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-45705
Aliases: GHSA-chxf-9368-fqcp
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-45705
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. In versions prior to 3.6.6 and 4.0.0-rc1, the find_line_delimiter() function in the multipart body parser performs an out-of-bounds read via strncmp() when searching for MIME boundary delimiters. After finding a -- pattern near the end of the body, the function compares delimiter.len bytes (typically 20-70) starting from a position at or past the logical end of the body buffer, reading past the body boundary. The bug triggers when a SIP message has Content-Type: multipart/mixed with a boundary parameter and its body contains -- within two to three bytes of the body's end without being followed by the actual boundary delimiter. This issue has been fixed in versions 3.6.6 and 4.0.0-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45705.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-chxf-9368-fqcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-45705
- https://github.com/OpenSIPS/opensips/commit/4d23613b65579b073784a07a65d3bf52443a4efb
- https://github.com/OpenSIPS/opensips/commit/5f103effaf5f372cccffe0b138f16998eba12668
