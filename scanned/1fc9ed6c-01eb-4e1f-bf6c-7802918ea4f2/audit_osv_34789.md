# [M] Rallly Has an IDOR Vulnerability in Participant Rename Function Allows Unauthorized Modification of Other Users’ Names

## Summary
Severity: Medium
Advisory: CVE-2025-65032
Aliases: GHSA-q9m7-chfx-43xw
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65032
Type: osv

## Details
Rallly is an open-source scheduling and collaboration tool. Prior to version 4.5.4, an Insecure Direct Object Reference (IDOR) vulnerability allows any authenticated user to change the display names of other participants in polls without being an admin or the poll owner. By manipulating the participantId parameter in a rename request, an attacker can modify another user’s name, violating data integrity and potentially causing confusion or impersonation attacks. This issue has been patched in version 4.5.4.

## References
- https://github.com/lukevella/rallly/releases/tag/v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65032.json
- https://github.com/lukevella/rallly/security/advisories/GHSA-q9m7-chfx-43xw
- https://nvd.nist.gov/vuln/detail/CVE-2025-65032
