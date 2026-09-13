# [H] Pterodactyl does not revoke SFTP access when server is deleted or permissions reduced

## Summary
Severity: High
Advisory: GHSA-8c39-xppg-479c
CVE: CVE-2025-68954
CWE: CWE-613
Ecosystem: Go, Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-06
Source: https://github.com/advisories/GHSA-8c39-xppg-479c
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.12.0
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.12.0

## Details
### Summary
Pterodactyl does not revoke _active_ SFTP connections when a user is removed from a server instance or has their permissions changes with respect to file access over SFTP. This allows a user that was already connected to SFTP to remain connected and access files even after their permissions are revoked.

### Details
When a user opens a connection to a server using the Wings SFTP server instance the permissions are checked and returned from the authentication API call made to the Panel. However, credentials are not checked again after the initial handshake. Thus, if a user is removed from a server in the panel or have their permissions modified, those permissions are not updated in the SFTP connection.

As a result, a user that has already gained access to a server's files via the SFTP subsystem will maintain those permissions until disconnected (via Wings restart, or a manual disconnection on their end).

> [!NOTE]
>
> This issue impacts the SFTP subsystem for server files specifically. There is no exposure of Wings private data, or any data outside of a server's local filesystem. Additionally, a user must have been _connected to SFTP at the time of their permissions being revoked_ in order for this issue to be exploited. If a user was not connected, they would not be able to connect once their permissions were reduced.

### Fix
Please upgrade to `wings@1.12.0` and `panel@1.12.0` to resolve this issue. Patches are available via the implementation PRs, but it is recommended to apply by upgrading the entire instance.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-8c39-xppg-479c
- https://nvd.nist.gov/vuln/detail/CVE-2025-68954
- https://github.com/pterodactyl/panel/commit/2bd9d8baddb0e0606e4a9d5be402f48678ac88d5
- https://github.com/pterodactyl/panel
- https://github.com/pterodactyl/panel/releases/tag/v1.12.0
