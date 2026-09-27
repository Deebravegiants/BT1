# [H] OpenEMR Has Disabled SSL Certificate Verification in HTTP Client

## Summary
Severity: High
Advisory: CVE-2025-67752
Aliases: GHSA-2g6h-725p-pqhp
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2025-67752
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 7.0.4, OpenEMR's HTTP client wrapper (`oeHttp`/`oeHttpRequest`) disables SSL/TLS certificate verification by default (`verify: false`), making all external HTTPS connections vulnerable to man-in-the-middle (MITM) attacks. This affects communication with government healthcare APIs and user-configurable external services, potentially exposing Protected Health Information (PHI). Version 7.0.4 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67752.json
- https://github.com/openemr/openemr/security/advisories/GHSA-2g6h-725p-pqhp
- https://nvd.nist.gov/vuln/detail/CVE-2025-67752
- https://github.com/openemr/openemr/commit/22f8e53e5769a88b7a16cb223bd197d044c84e5a
