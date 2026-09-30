# [C] Relay Server WebSocket authentication bypass when token is omitted

## Summary
Severity: Critical
Advisory: CVE-2026-42889
Aliases: GHSA-9vp9-8q9j-8mqm
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-42889
Type: osv

## Details
Relay adds real-time collaboration to Obsidian. Relay Server versions 0.9.0 through 0.9.6 contain an authentication bypass in the multi-document WebSocket endpoints. When authentication is configured, WebSocket connections without a token query parameter were incorrectly treated as having full server permissions. An unauthenticated network attacker who knows or guesses a document ID could connect to the document sync WebSocket and read or modify document contents without a valid document token. This vulnerability is fixed in 0.9.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42889.json
- https://github.com/No-Instructions/relay-server/security/advisories/GHSA-9vp9-8q9j-8mqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-42889
