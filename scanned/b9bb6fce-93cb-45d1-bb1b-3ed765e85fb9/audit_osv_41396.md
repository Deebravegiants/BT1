# [H] CVE-2026-60009

## Summary
Severity: High
Advisory: CVE-2026-60009
Aliases: GHSA-62f6-wcvg-54h3
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-60009
Type: osv

## Details
In Eclipse Theia versions up to and including 1.73.1, the `@theia/filesystem` backend binds `POST /file-upload` in every filesystem-enabled deployment. The handler takes an attacker-supplied absolute path from the multipart `uri` field and calls `fs.move(tmp, target, { overwrite: true })` with no workspace confinement and no authentication. In browser (non-Electron) deployments the connection token is enforced only on WebSocket upgrades; the HTTP middleware in `@theia/core` re-issues the cookie and calls `next()` without rejecting tokenless HTTP requests. Because `multipart/form-data` is a CORS-safelisted request type, a cross-origin web page can trigger the write with no preflight and no credentials, resulting in an unauthenticated arbitrary file write outside the workspace to any absolute path the backend process can write. This can escalate to remote code execution, for example by overwriting a startup-executed file such as `~/.bashrc`. Electron mode uses a separate `ElectronSecurityToken` and is not affected via this path.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/177
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60009.json
- https://github.com/eclipse-theia/theia/security/advisories/GHSA-62f6-wcvg-54h3
- https://nvd.nist.gov/vuln/detail/CVE-2026-60009
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/595
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/595
