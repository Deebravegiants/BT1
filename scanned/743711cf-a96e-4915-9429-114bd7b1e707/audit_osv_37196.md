# [C] SuiteCRM Authenticated Remote Code Execution via Unsafe Deserialization in SavedSearch Filter Processing

## Summary
Severity: Critical
Advisory: CVE-2026-29109
Aliases: GHSA-mhq2-277m-6w24
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-29109
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Versions up to and including 8.9.2 contain an unsafe deserialization vulnerability in the SavedSearch filter processing component that allows an authenticated administrator to execute arbitrary system commands on the server. `FilterDefinitionProvider.php` calls `unserialize()` on user-controlled data from the `saved_search.contents` database column without restricting instantiable classes. Version 8.9.3 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29109.json
- https://github.com/SuiteCRM/SuiteCRM-Core/security/advisories/GHSA-mhq2-277m-6w24
- https://nvd.nist.gov/vuln/detail/CVE-2026-29109
