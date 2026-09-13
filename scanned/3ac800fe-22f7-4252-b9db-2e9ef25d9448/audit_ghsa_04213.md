# [M] Probo has an open redirect bypass via path normalization

## Summary
Severity: Medium
Advisory: GHSA-x7qq-m748-8p2c
CVE: CVE-2026-49820
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-x7qq-m748-8p2c
Type: github-advisory

## Affected
- Go: `go.probo.inc/probo` — affected >=0 <0.204.0

## Details
### Impact
Probo's `saferedirect` package validates redirect URLs used across authentication flows (OIDC, SAML, session transfer, OAuth connectors, and trust-center magic links). The validator only inspected the second character of relative paths, so a URL like `/../\evil.com` passed validation because the second character is `.`. Go's `http.Redirect` normalizes this path to `/\evil.com` before setting the `Location` header. Browsers can interpret the backslash as a host separator and redirect the user to an external domain (`https://evil.com`), bypassing the intended same-origin restriction. This enables open-redirect phishing: an attacker can craft a `continue` parameter (or embed a malicious URL in a session-transfer token) that appears to originate from a trusted Probo domain but redirects victims elsewhere.

### Patches
Fixed in `go.probo.inc/probo` by normalizing relative paths with `path.Clean` before validation, rejecting backslashes (including
percent-encoded `%5c`) anywhere in the path, and re-checking the normalized result for protocol-relative and backslash prefixes.

Self-hosted deployments should upgrade to **probod v0.194.1** or later.

SaaS deployments on getprobo.com are patched.

### Workarounds
No practical workaround for self-hosted installations. Upgrade to the patched release.

## References
- https://github.com/getprobo/probo/security/advisories/GHSA-x7qq-m748-8p2c
- https://github.com/getprobo/probo
- https://github.com/getprobo/probo/blob/main/SECURITY_NOTES.md
