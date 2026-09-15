# [H] Path Traversal (Arbitrary File Delete) in Chamilo LMS

## Summary
Severity: High
Advisory: CVE-2026-31939
Aliases: GHSA-8q8c-v75x-q2hx
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-31939
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38, there is a path traversal in main/exercise/savescores.php leading to arbitrary file feletion. User input from $_REQUEST['test'] is concatenated directly into filesystem path without canonicalization or traversal checks. This vulnerability is fixed in 1.11.38.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31939.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-8q8c-v75x-q2hx
- https://nvd.nist.gov/vuln/detail/CVE-2026-31939
- https://github.com/chamilo/chamilo-lms/commit/4dddcc19d36119da27b7c49eb84a035800abae78
