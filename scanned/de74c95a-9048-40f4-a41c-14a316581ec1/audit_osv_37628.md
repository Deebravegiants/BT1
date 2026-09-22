# [C] OpenEMR has Remote Code Execution in backup functionality

## Summary
Severity: Critical
Advisory: CVE-2026-32238
Aliases: GHSA-6pmc-3xm7-pm86
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-32238
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Versions prior to 8.0.0.2 contain a Command injection vulnerability in the backup functionality that can be exploited by authenticated attackers. The vulnerability exists due to insufficient input validation in the backup functionality. Version 8.0.0.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32238.json
- https://github.com/openemr/openemr/security/advisories/GHSA-6pmc-3xm7-pm86
- https://nvd.nist.gov/vuln/detail/CVE-2026-32238
- https://github.com/openemr/openemr/commit/7bc7bd077a624e205daed17658de41af6070ef73
