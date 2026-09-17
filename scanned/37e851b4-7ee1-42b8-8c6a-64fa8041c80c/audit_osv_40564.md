# [C] Termix: IDOR — Authenticated user can fetch SSH passwords for hosts owned by other users

## Summary
Severity: Critical
Advisory: CVE-2026-53548
Aliases: GHSA-j6h8-mww6-pgw6
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-53548
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to 2.6.1, the GET /host/db/host/:id/password endpoint in src/backend/database/routes/host.ts accepts an authenticated user's numeric host ID and the field=password or field=sudoPassword query without enforcing host ownership during credential resolution. A failed requester-scoped lookup can resolve the host with the owner's context and return the owner's plaintext credential, allowing any authenticated user with a valid JWT to enumerate sequential hosts.id values and retrieve SSH or sudo passwords belonging to other users. The disclosed credentials can then be used to access and control managed systems outside the Termix instance. This issue is fixed in version 2.6.1.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53548.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-j6h8-mww6-pgw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-53548
- https://github.com/Termix-SSH/Termix/commit/52f4e51ae03b5b8d2608e1383e2ccf79d290132b
- https://github.com/Termix-SSH/Termix/pull/874
