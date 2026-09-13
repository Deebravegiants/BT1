# [M] 9Router: Kiro region injection allows authenticated SSRF with Authorization header forwarding

## Summary
Severity: Medium
Advisory: CVE-2026-56678
Aliases: GHSA-6mwv-4mrm-5p3m
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-56678
Type: osv

## Details
9Router is an AI router & token saver. Prior to 0.5.6, the Kiro API-key validation endpoint POST /api/oauth/kiro/api-key builds an upstream URL using a user-controlled region value, allowing an authenticated attacker to supply a crafted region such as kiro-canary.local:8443# and cause 9Router to send the Kiro validation request to an attacker-controlled host while forwarding the submitted Kiro API key as an Authorization header. This issue is fixed in version 0.5.6.

## References
- https://github.com/decolua/9router/releases/tag/v0.5.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56678.json
- https://github.com/decolua/9router/security/advisories/GHSA-6mwv-4mrm-5p3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-56678
- https://github.com/decolua/9router/commit/126aa244c5b51b74ab8c7594e3418fcf4437bf6f
