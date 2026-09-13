# [H] Combodo iTop: Authentication bypass in exec.php allows PHP file execution

## Summary
Severity: High
Advisory: CVE-2026-34741
Aliases: GHSA-36h9-5qw2-jcc6
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-34741
Type: osv

## Details
Combodo iTop is a web based IT service management tool. Prior to 3.2.3, authentication bypass allows unauthenticated remote attackers to execute arbitrary PHP files from the env-production directory on a new iTop instance in the production environment. This issue has been fixed in version 3.2.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34741.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-36h9-5qw2-jcc6
- https://nvd.nist.gov/vuln/detail/CVE-2026-34741
- https://github.com/Combodo/iTop/commit/4fe61cbdc779cb5576395d4ae8be31f9fbc7306c
