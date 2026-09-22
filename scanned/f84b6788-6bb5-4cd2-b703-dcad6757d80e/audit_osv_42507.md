# [H] Nesquena Hermes WebUI Arbitrary File Deletion via Unvalidated session_id

## Summary
Severity: High
Advisory: CVE-2026-6832
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-6832
Type: osv

## Details
Hermes WebUI contains an arbitrary file deletion vulnerability in the /api/session/delete endpoint that allows authenticated attackers to delete files outside the session directory by supplying an absolute path or path traversal payload in the session_id parameter. Attackers can exploit unvalidated session identifiers to construct paths that bypass the SESSION_DIR boundary and delete writable JSON files on the host system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6832.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.50.132
- https://github.com/nesquena/hermes-webui/releases/tag/v0.50.32
- https://nvd.nist.gov/vuln/detail/CVE-2026-6832
- https://www.vulncheck.com/advisories/nesquena-hermes-webui-arbitrary-file-deletion-via-unvalidated-session-id
- https://github.com/nesquena/hermes-webui/pull/409
- https://github.com/nesquena/hermes-webui/pull/412
- https://github.com/nesquena/hermes-webui/commit/3cc5839bf303fa6758bfdac538507407a2929655
