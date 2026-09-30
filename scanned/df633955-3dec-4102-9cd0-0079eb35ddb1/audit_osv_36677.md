# [C] OpenEMR has SQL Injection in Patient API Sort Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-24908
Aliases: GHSA-rcc2-45v3-qmqm
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-24908
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, an SQL injection vulnerability in the Patient REST API endpoint allows authenticated users with API access to execute arbitrary SQL queries through the `_sort` parameter. This could potentially lead to database access, PHI (Protected Health Information) exposure, and credential compromise. The issue occurs when user-supplied sort field names are used in ORDER BY clauses without proper validation or identifier escaping. Version 8.0.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24908.json
- https://github.com/openemr/openemr/security/advisories/GHSA-rcc2-45v3-qmqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-24908
- https://github.com/openemr/openemr/commit/943e23cad6e979f87cdf168807fce2a7b32dd194
