# [M] n8n allows open redirects via the /signin endpoint

## Summary
Severity: Medium
Advisory: GHSA-5vj6-wjr7-5v9f
CVE: CVE-2025-49592
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-27
Source: https://github.com/advisories/GHSA-5vj6-wjr7-5v9f
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.98.0

## Details
### Impact

This is an Open Redirect (CWE-601) vulnerability in the login flow of n8n. Authenticated users can be redirected to untrusted, attacker-controlled domains after logging in, by crafting malicious URLs with a misleading redirect query parameter.

This may lead to:

- Phishing attacks by impersonating the n8n UI on lookalike domains (e.g., n8n.local.evil.com)
- Credential or 2FA theft if users are tricked into re-entering sensitive information
- Reputation risk due to the visual similarity between attacker-controlled domains and trusted ones

The vulnerability affects anyone hosting n8n and exposing the `/signin` endpoint to users.

### Patches

The issue has been patched in [1.98.0](https://github.com/n8n-io/n8n/releases/tag/n8n%401.98.0).
All users should upgrade to this version or later.

The fix introduces strict origin validation for redirect URLs, ensuring only same-origin or relative paths are allowed after login.

Patch commit: https://github.com/n8n-io/n8n/pull/16034

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-5vj6-wjr7-5v9f
- https://nvd.nist.gov/vuln/detail/CVE-2025-49592
- https://github.com/n8n-io/n8n/pull/16034
- https://github.com/n8n-io/n8n/commit/4865d1e360a0fe7b045e295b5e1a29daad12314e
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n%401.98.0
