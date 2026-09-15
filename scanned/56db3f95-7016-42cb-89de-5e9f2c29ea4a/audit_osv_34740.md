# [H] SuiteCRM: Authenticated SQL Injection Possible in Reschedule Call Module

## Summary
Severity: High
Advisory: CVE-2025-64488
Aliases: GHSA-5v53-v44q-ww2c
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-64488
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. In versions 7.14.7 and below and 8.0.0-beta.1 through 8.9.0 8.0.0-beta.1, an attacker can craft a malicious call_id that alters the logic of the SQL query or injects arbitrary SQL. An attack can lead to unauthorized data access and data ex-filtration, complete database compromise, and other various issues. This issue is fixed in versions 7.14.8 and 8.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64488.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-5v53-v44q-ww2c
- https://nvd.nist.gov/vuln/detail/CVE-2025-64488
- https://github.com/SuiteCRM/SuiteCRM-Core/commit/30277cfe69755f7360a23d4805e06a5c38f14131
- https://github.com/SuiteCRM/SuiteCRM/commit/40da2845a170832a4e9e9fa0ebe731f8c34de42d
