# [C] Parse Dashboard is Missing Authorization for its Agent Endpoint

## Summary
Severity: Critical
Advisory: GHSA-cvwj-6c9h-jg6v
CVE: CVE-2026-27608
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-cvwj-6c9h-jg6v
Type: github-advisory

## Affected
- npm: `parse-dashboard` — affected >=7.3.0-alpha.42 <9.0.0-alpha.8

## Details
### Impact

The AI Agent API endpoint (`POST /apps/:appId/agent`) does not enforce authorization. Authenticated users scoped to specific apps can access any other app's agent endpoint by changing the app ID in the URL. Read-only users are given the full master key instead of the read-only master key and can supply write permissions in the request body to perform write and delete operations.

Affected are only dashboards with `agent` configuration enabled.

### Patches

The fix adds per-app authorization checks and restricts read-only users to the `readOnlyMasterKey` with write permissions stripped server-side.

### Workarounds

Remove the `agent` configuration block from your dashboard configuration. Dashboards without an `agent` config are not affected.

### Resources

- GitHub advisory: https://github.com/parse-community/parse-dashboard/security/advisories/GHSA-cvwj-6c9h-jg6v
- Fixed in: https://github.com/parse-community/parse-dashboard/releases/tag/9.0.0-alpha.8

## References
- https://github.com/parse-community/parse-dashboard/security/advisories/GHSA-cvwj-6c9h-jg6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-27608
- https://github.com/parse-community/parse-dashboard
- https://github.com/parse-community/parse-dashboard/releases/tag/9.0.0-alpha.8
