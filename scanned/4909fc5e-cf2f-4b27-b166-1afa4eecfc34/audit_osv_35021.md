# [H] OpenEMR Vulnerable to Broken Access Control in Profile Edit Endpoint

## Summary
Severity: High
Advisory: CVE-2025-67645
Aliases: GHSA-vjmv-cf46-gffv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2025-67645
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Versions prior to 7.0.4 have a broken access control in the Profile Edit endpoint. An authenticated normal user can modify the request parameters (pubpid / pid) to reference another user’s record; the server accepts the modified IDs and applies the changes to that other user’s profile. This allows one user to alter another user’s profile data (name, contact info, etc.), and could enable account takeover. Version 7.0.4 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67645.json
- https://github.com/openemr/openemr/security/advisories/GHSA-vjmv-cf46-gffv
- https://nvd.nist.gov/vuln/detail/CVE-2025-67645
- https://github.com/openemr/openemr/commit/e2a682ee71aac71a9f04ae566f4ffca10052bc4a
