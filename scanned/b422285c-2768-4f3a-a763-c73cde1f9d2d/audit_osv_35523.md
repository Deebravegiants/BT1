# [H] CVE-2026-10054

## Summary
Severity: High
Advisory: CVE-2026-10054
Aliases: GHSA-78g8-vm3p-97c6
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-10054
Type: osv

## Details
In affected versions of Eclipse Theia (1.8.1 and later), the browser backend exposes privileged terminal RPC over WebSocket (/services/shell-terminal, /services/terminals/:id) without service-level authentication.




WebSocket origin validation in @theia/core is fail-open: connections are accepted when the Origin header is missing or when no THEIA_HOSTS allowlist is configured (the default). The Socket.IO integration additionally replaces the real Origin header with a client-supplied fix-origin header that an attacker can control or omit.




As a result, a foreign-origin web page visited by a user with a running Theia instance can open the /services WebSocket namespace, invoke terminal creation, attach to the resulting terminal data channel, execute arbitrary OS commands, and read their output. This affects both local developer setups (drive-by attack) and hosted or tunneled deployments without strong external authentication.




A fix is in development that enforces same-origin validation by default, removes trust in the fix-origin header, gates HTTP and WebSocket access on a SameSite=Strict; HttpOnly connection-token cookie, and sanitizes shell terminal creation options.

## References
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/376
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10054.json
- https://github.com/eclipse-theia/theia/security/advisories/GHSA-78g8-vm3p-97c6
- https://nvd.nist.gov/vuln/detail/CVE-2026-10054
