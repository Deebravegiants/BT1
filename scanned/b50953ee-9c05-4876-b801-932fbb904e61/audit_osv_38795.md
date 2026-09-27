# [M] SysReptor: Read-write access to personal notes by sharing-link creation with no authorization in SysReptor Professional

## Summary
Severity: Medium
Advisory: CVE-2026-42291
Aliases: GHSA-pcpr-q2qj-3v43
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42291
Type: osv

## Details
SysReptor is a fully customizable pentest reporting platform. From version 2026.4 to before version 2026.27, the endpoints for reading and creating sharing links for personal notes is not properly authorized. This allows authenticated attackers who obtain the note ID of victim users to list and create sharing links to those users' personal notes. This gives attackers read and write access to notes of other users. This exploit works in both SysReptor Professional and Community. In Community it has, however, no impact because all users have superuser permissions and can list personal notes of other users at /admin/pentests/usernotebookpage/. This issue has been patched in version 2026.27.

## References
- https://github.com/Syslifters/sysreptor/releases/tag/2026.27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42291.json
- https://github.com/Syslifters/sysreptor/security/advisories/GHSA-pcpr-q2qj-3v43
- https://nvd.nist.gov/vuln/detail/CVE-2026-42291
