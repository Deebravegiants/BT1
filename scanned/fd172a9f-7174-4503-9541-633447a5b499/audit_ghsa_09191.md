# [H] Crabbox: authentication bypass vulnerability that allows impersonation of others by spoofing identity headers

## Summary
Severity: High
Advisory: GHSA-4g9m-rffv-h6wq
CVE: CVE-2026-8621
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-4g9m-rffv-h6wq
Type: github-advisory

## Affected
- Go: `github.com/openclaw/crabbox` — affected >=0 <0.12.0

## Details
Crabbox prior to v0.12.0 contains an authentication bypass vulnerability that allows non-admin shared-token callers to impersonate other owners or organizations by spoofing identity headers. Attackers can inject malicious X-Crabbox-Owner and X-Crabbox-Org headers in requests authenticated with a shared token to bypass authorization checks and access owner/org-scoped lease operations belonging to victim accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8621
- https://github.com/openclaw/crabbox/pull/70
- https://github.com/openclaw/crabbox/commit/b657323f1d1c954cefc8444571fa6c45a8896e7f
- https://github.com/openclaw/crabbox
- https://github.com/openclaw/crabbox/releases/tag/v0.12.0
- https://www.vulncheck.com/advisories/crabbox-authentication-bypass-via-header-spoofing
