# [C] Parse Dashboard has incomplete authentication on AI Agent endpoint

## Summary
Severity: Critical
Advisory: GHSA-qwc3-h9mg-4582
CVE: CVE-2026-27595
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-qwc3-h9mg-4582
Type: github-advisory

## Affected
- npm: `parse-dashboard` — affected >=7.3.0-alpha.42 <9.0.0-alpha.8

## Details
### Impact

The AI Agent API endpoint (POST `/apps/:appId/agent`) lacks authentication. Unauthenticated remote attackers can send requests to the endpoint and perform arbitrary database operations against any connected Parse Server using the master key.

### Patches

The fix adds authentication middleware to the agent endpoint.

### Workarounds

Remove the `agent` configuration block from your dashboard configuration. Dashboards without an `agent` config are not affected.

### Resources

- GitHub advisory: https://github.com/parse-community/parse-dashboard/security/advisories/GHSA-qwc3-h9mg-4582
- Fixed in: https://github.com/parse-community/parse-dashboard/releases/tag/9.0.0-alpha.8

## References
- https://github.com/parse-community/parse-dashboard/security/advisories/GHSA-qwc3-h9mg-4582
- https://nvd.nist.gov/vuln/detail/CVE-2026-27595
- https://github.com/parse-community/parse-dashboard/commit/f92a9ef5246d57e51696bd881a15f3b133b2bb50
- https://github.com/parse-community/parse-dashboard
- https://github.com/parse-community/parse-dashboard/releases/tag/9.0.0-alpha.8
