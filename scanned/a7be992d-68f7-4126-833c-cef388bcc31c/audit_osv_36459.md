# [C] OpenEMR has SQL Injection in Immunization Search/Report

## Summary
Severity: Critical
Advisory: CVE-2026-23627
Aliases: GHSA-x3hw-rwrg-v25h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-23627
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, an SQL injection vulnerability in the Immunization module allows any authenticated user to execute arbitrary SQL queries, leading to complete database compromise, PHI exfiltration, credential theft, and potential remote code execution. The vulnerability exists because user-supplied `patient_id` values are directly concatenated into SQL WHERE clauses without parameterization or escaping. Version 8.0.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23627.json
- https://github.com/openemr/openemr/security/advisories/GHSA-x3hw-rwrg-v25h
- https://nvd.nist.gov/vuln/detail/CVE-2026-23627
- https://github.com/openemr/openemr/commit/cbf4ea4345b14a6c8362201e30c74ffb0949cdb1
