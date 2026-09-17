# [H] Termix has a File-Manager Session Hijack via Missing Ownership Check (IDOR)

## Summary
Severity: High
Advisory: CVE-2026-45743
Aliases: GHSA-5fqh-77cr-jj5x
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-45743
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. 16 file-manager endpoints in Termix prior to version 2.3.2 do not verify that the requesting user owns the SSH session identified by `sessionId`. An authenticated attacker who knows or guesses another user's active `sessionId` can read, write, delete, download, and execute files on the victim's connected SSH host. Version 2.3.2 patches the issue.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45743.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-5fqh-77cr-jj5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-45743
