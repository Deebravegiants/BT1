# [H] MCP DNS-rebinding origin check in AshAi is bypassed by a spoofed X-Forwarded-Proto header

## Summary
Severity: High
Advisory: CVE-2026-81315
Aliases: EEF-CVE-2026-81315, GHSA-c92r-f3rr-q49h
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-81315
Type: osv

## Details
Origin Validation Error vulnerability in ash-project ash_ai allows a malicious web page to bypass the MCP server's DNS-rebinding protection and issue cross-site requests to a user's local MCP server with that user's actor.

In AshAi.Mcp.Server, with the default allowed_origins: nil, origin_allowed?/3 accepts an origin when uri.host == conn.host and the forwarded scheme is https. Both values are attacker-controlled: conn.host comes from the Host header and the scheme is read from the raw x-forwarded-proto header with no trusted-proxy check. Under DNS rebinding the browser sends the attacker's origin and a matching host, and page JavaScript may set X-Forwarded-Proto: https, so the check passes with no TLS or proxy involved. The fix trusts only localhost origins by default; other origins require an explicit allowed_origins allowlist.

This issue affects ash_ai: from 0.8.0 before 1.0.0.

## References
- https://cna.erlef.org/cves/CVE-2026-81315.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-81315
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81315.json
- https://github.com/ash-project/ash_ai/security/advisories/GHSA-c92r-f3rr-q49h
- https://nvd.nist.gov/vuln/detail/CVE-2026-81315
- https://github.com/ash-project/ash_ai/commit/28af68d73134df0b8fb3aa6ab03e8fd795b07c21
- https://github.com/ash-project/ash_ai
