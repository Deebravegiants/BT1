# [H] CVE-2026-61891

## Summary
Severity: High
Advisory: CVE-2026-61891
Aliases: GHSA-qqc8-9538-25v4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-61891
Type: osv

## Details
In Eclipse Theia versions up to and including 1.73.1, the `@theia/filesystem` backend exposes HTTP file-download endpoints (`GET /file`, `GET /files/`, `PUT /files/`) that convert a client-supplied URI directly to a filesystem path and stream the file, without confining it to the workspace or any allow-listed root. In browser (non-Electron) deployments the connection token is enforced only on WebSocket upgrades; the HTTP middleware in `@theia/core` re-issues the cookie and calls `next()` without rejecting tokenless HTTP requests, so these endpoints are reachable without a valid token. As a result an unauthenticated client can read any file readable by the backend process, including files outside the opened workspace (for example `/etc/hosts`, SSH keys, or tokens). Electron mode uses a separate `ElectronSecurityToken` and is not affected via this path.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/176
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61891.json
- https://github.com/eclipse-theia/theia/security/advisories/GHSA-qqc8-9538-25v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-61891
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/570
