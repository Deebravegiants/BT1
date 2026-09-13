# [H] OpenEMR has a SQL Injection Vulnerability in patient selection

## Summary
Severity: High
Advisory: CVE-2026-33910
Aliases: GHSA-x32c-xj5g-7jx7
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-33910
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Versions up to and including 8.0.0.2 contain a SQL injection vulnerability in the patient selection feature that can be exploited by authenticated attackers. The vulnerability exists due to insufficient input validation in the patient selection feature. Version 8.0.0.3 contains a patch.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33910.json
- https://github.com/openemr/openemr/security/advisories/GHSA-x32c-xj5g-7jx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33910
- https://github.com/openemr/openemr/commit/73db3264aed253684532839380cae3b0a56c83d2
