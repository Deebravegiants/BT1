# [M] OpenEMR has Broken Access Control on Care Coordination Module

## Summary
Severity: Medium
Advisory: CVE-2026-25127
Aliases: GHSA-69cv-rv28-4g85
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25127
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, the server does not properly validate user permission. Unauthorized users can view the information of authorized users. Version 8.0.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25127.json
- https://github.com/openemr/openemr/security/advisories/GHSA-69cv-rv28-4g85
- https://nvd.nist.gov/vuln/detail/CVE-2026-25127
- https://github.com/openemr/openemr/commit/ad902d6892482fff2e3c56bfb15597df8b6c3beb
