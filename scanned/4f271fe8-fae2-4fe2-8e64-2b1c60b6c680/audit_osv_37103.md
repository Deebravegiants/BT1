# [H] Textream Cross-Site WebSocket Hijacking (CSWSH) vulnerability

## Summary
Severity: High
Advisory: CVE-2026-28403
Aliases: GHSA-wr3v-x247-337w
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2026-28403
Type: osv

## Details
Textream is a free macOS teleprompter app. Prior to version 1.5.1, the `DirectorServer` WebSocket server (`ws://127.0.0.1:<httpPort+1>`) accepts connections from any origin without validating the HTTP `Origin` header during the WebSocket handshake. A malicious web page visited in the same browser session can silently connect to the local WebSocket server and send arbitrary `DirectorCommand` payloads, allowing full remote control of the teleprompter content. Version 1.5.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28403.json
- https://github.com/f/textream/security/advisories/GHSA-wr3v-x247-337w
- https://nvd.nist.gov/vuln/detail/CVE-2026-28403
- https://github.com/f/textream/commit/f5ebad82750b9313386c34af8f0ede50c213a8a0
