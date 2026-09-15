# [H] Parse Dashboard is Missing CSRF Protection for its Agent Endpoint

## Summary
Severity: High
Advisory: GHSA-3534-xp88-25rc
CVE: CVE-2026-27609
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-3534-xp88-25rc
Type: github-advisory

## Affected
- npm: `parse-dashboard` — affected >=7.3.0-alpha.42 <9.0.0-alpha.8

## Details
### Impact

The AI Agent API endpoint (`POST /apps/:appId/agent`) lacks CSRF protection. An attacker can craft a malicious page that, when visited by an authenticated dashboard user, submits requests to the agent endpoint using the victim's session.

### Patches

The fix adds CSRF middleware to the agent endpoint and embeds a CSRF token in the dashboard page.

### Workarounds

Remove the `agent` configuration block from your dashboard configuration. Dashboards without an `agent` config are not affected.

### Resources

- GitHub advisory: https://github.com/parse-community/parse-dashboard/security/advisories/GHSA-3534-xp88-25rc
- Fixed in: https://github.com/parse-community/parse-dashboard/releases/tag/9.0.0-alpha.8

## References
- https://github.com/parse-community/parse-dashboard/security/advisories/GHSA-3534-xp88-25rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27609
- https://github.com/parse-community/parse-dashboard
- https://github.com/parse-community/parse-dashboard/releases/tag/9.0.0-alpha.8
