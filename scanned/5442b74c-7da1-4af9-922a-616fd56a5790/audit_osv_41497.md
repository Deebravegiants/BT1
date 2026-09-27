# [H] Pterodactyl Wings SFTP write path does not enforce disk quota, allowing node-wide disk exhaustion

## Summary
Severity: High
Advisory: CVE-2026-61617
Aliases: GHSA-8j54-xcwx-597p
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-61617
Type: osv

## Details
Wings is the server control plane for the Pterodactyl game-server management panel. In versions up to and including 1.13.2, the SFTP write path does not enforce a server's disk quota during a transfer, allowing a tenant with SFTP write access to a single server to exhaust the host node's physical disk and take down every server on it. Wings checks available space only once, as a boolean, when the write handle is opened, using a stale cached usage value and without knowing the size of the incoming data, and it then returns a raw, unaccounted file handle that is never re-checked as the transfer proceeds. A single upload can therefore be written without bound, far beyond the configured disk limit, until the node's disk is full, and because a server stopped for exceeding its limit is not treated as suspended, SFTP writes are still accepted even after the quota is already exceeded. This issue is fixed in version 1.13.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61617.json
- https://github.com/pterodactyl/wings/security/advisories/GHSA-8j54-xcwx-597p
- https://nvd.nist.gov/vuln/detail/CVE-2026-61617
- https://github.com/pterodactyl/wings/commit/da1a216cfff5867fa66be32cb1edb93e37fd71ff
