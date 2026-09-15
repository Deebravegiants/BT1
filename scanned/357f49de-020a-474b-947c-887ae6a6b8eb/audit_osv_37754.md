# [M] Chamilo LMS has an IDOR in REST API Stats Endpoint Exposes Any User's Learning Data

## Summary
Severity: Medium
Advisory: CVE-2026-33141
Aliases: GHSA-j2pr-2r5w-jrpj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33141
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 2.0.0-RC.3, an Insecure Direct Object Reference (IDOR) vulnerability in the REST API stats endpoint allows any authenticated user (including low-privilege students with ROLE_USER) to read any other user's learning progress, certificates, and gradebook scores for any course, without enrollment or supervisory relationship. This vulnerability is fixed in 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33141.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-j2pr-2r5w-jrpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33141
- https://github.com/chamilo/chamilo-lms/commit/792ba05953470ca971617fe2674ed14c1479fa80
