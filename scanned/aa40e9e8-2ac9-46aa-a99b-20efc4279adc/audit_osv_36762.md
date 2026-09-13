# [M] HedgeDoc security headers for uploaded files were not working

## Summary
Severity: Medium
Advisory: CVE-2026-25642
Aliases: GHSA-x74j-jmf9-534w
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2026-25642
Type: osv

## Details
HedgeDoc is an open source, real-time, collaborative, markdown notes application. Prior to 1.10.6, files served below the /uploads/ endpoint did not use a more strict security-policy. This resulted in a too open Content-Security-Policy and furthermore opened the possibility to host malicious interactive web content (such as fake login forms) using SVG files. This vulnerability is fixed in 1.10.6.

## References
- https://github.com/hedgedoc/hedgedoc/releases/tag/1.10.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25642.json
- https://github.com/hedgedoc/hedgedoc/security/advisories/GHSA-x74j-jmf9-534w
- https://nvd.nist.gov/vuln/detail/CVE-2026-25642
- https://github.com/hedgedoc/hedgedoc/commit/74daa0e7a1cbfafd9aeb255eaf064dfe47cd401c
- https://github.com/hedgedoc/hedgedoc/commit/b930fe04cee92cd4723044030bb59c36781c7137
