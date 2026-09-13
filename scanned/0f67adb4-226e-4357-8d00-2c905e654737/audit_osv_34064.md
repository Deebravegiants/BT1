# [M] OpenEMR may expose Contents of Clinical Notes and Care Planto users who do not have Sensitivities=high privilege

## Summary
Severity: Medium
Advisory: CVE-2025-54373
Aliases: GHSA-739g-6m63-p7fr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2025-54373
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Versions prior to 7.0.4 have a vulnerability where sensitive data is unintentionally revealed to unauthorized parties. Contents of Clinical Notes and Care Plan, where an encounter has Sensitivity=high, can be viewed and changed by users who do not have Sensitivities=high privilege. Version 7.0.4 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54373.json
- https://github.com/openemr/openemr/security/advisories/GHSA-739g-6m63-p7fr
- https://nvd.nist.gov/vuln/detail/CVE-2025-54373
- https://github.com/openemr/openemr/commit/aef3d1c85d9ff2f28d3d361d2818aee79b6dcd33
