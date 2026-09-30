# [H] TypeBot: SSRF Protection Bypass via DNS-Resolved Hostnames in Webhook / HTTP Request Validation

## Summary
Severity: High
Advisory: CVE-2026-34207
Aliases: GHSA-grcc-6x37-wwgp
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-34207
Type: osv

## Details
TypeBot is a chatbot builder tool. In versions prior to 3.16.0, SSRF protection for Webhook / HTTP Request blocks validates only the URL string, blocked hostname literals, and literal IP formats. It does not resolve DNS before allowing the request. As a result, a hostname such as ssrf-repro.example that resolves to 127.0.0.1, 169.254.169.254, or RFC1918/private space passes validation and is later fetched by the backend HTTP client. This enables server-side request forgery to loopback, cloud metadata, and private network targets. This issue has been resolved in version 3.16.0.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34207.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-grcc-6x37-wwgp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34207
- https://github.com/baptisteArno/typebot.io/commit/23818bb0e54db23c456ee3fa6b12d82b2af848b8
