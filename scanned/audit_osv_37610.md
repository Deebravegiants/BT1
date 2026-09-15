# [H] SQL Injection Vulnerability in ajax graphs library (OpenEMR)

## Summary
Severity: High
Advisory: CVE-2026-32127
Aliases: GHSA-v8q6-h79f-736x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-32127
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0.1, OpenEMR contains a SQL injection vulnerability in the ajax graphs library that can be exploited by authenticated attackers. The vulnerability exists due to insufficient input validation in the ajax graphs library. This vulnerability is fixed in 8.0.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32127.json
- https://github.com/openemr/openemr/security/advisories/GHSA-v8q6-h79f-736x
- https://nvd.nist.gov/vuln/detail/CVE-2026-32127
