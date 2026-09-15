# [M] OpenEMR Vulnerable to SQL Injection via Unsanitized Variables in MedEx Recall/Reminder Processing

## Summary
Severity: Medium
Advisory: CVE-2026-33909
Aliases: GHSA-6vx2-w9hw-prqj
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-33909
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, several variables in the MedEx recall/reminder processing code are concatenated directly into SQL queries without parameterization or type casting, enabling SQL injection. Version 8.0.0.3 contains a patch.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33909.json
- https://github.com/openemr/openemr/security/advisories/GHSA-6vx2-w9hw-prqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33909
- https://github.com/openemr/openemr/commit/3d11d2fc1622147d4aa6fbca31a471e7402ffc65
