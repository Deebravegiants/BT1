# [M] Nextcloud: ACL Rename Permission Bypass in Team Folders Allows Unauthorized File Renames

## Summary
Severity: Medium
Advisory: CVE-2026-45264
Aliases: GHSA-wx2x-822r-rvmf
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45264
Type: osv

## Details
Nextcloud is an open source content collaboration platform. From versions 17.0.0 to before 17.0.15, 18.0.0 to before 18.1.12, 19.0.0 to before 19.1.16, 20.0.0 to before 20.1.11, and 21.0.0 to before 21.0.4, a user with READ and CREATE permission, but no UPDATE permission for a team folder can rename files in the team folder. This issue has been patched in versions 17.0.15, 18.1.12, 19.1.16, 20.1.11, and 21.0.4.

## References
- https://hackerone.com/reports/3540673
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45264.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wx2x-822r-rvmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-45264
- https://github.com/nextcloud/groupfolders/pull/4361
