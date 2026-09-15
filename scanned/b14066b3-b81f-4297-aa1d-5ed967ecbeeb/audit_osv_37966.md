# [M] OpenEMR has Improper ACL On Import/Export Popup

## Summary
Severity: Medium
Advisory: CVE-2026-34051
Aliases: GHSA-54m8-wpg9-9665
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-34051
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Versions prior to 8.0.0.3 have an improper access control on the Import/Export functionality, allowing unauthorized users to perform import and export actions through direct request manipulation despite UI restrictions. This can lead to unauthorized data access, bulk data extraction, and manipulation of system data. Version 8.0.0.3 contains a fix.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34051.json
- https://github.com/openemr/openemr/security/advisories/GHSA-54m8-wpg9-9665
- https://nvd.nist.gov/vuln/detail/CVE-2026-34051
- https://github.com/openemr/openemr/commit/81c097f7852fc60d45adf6c13baa86cd0a1b400b
