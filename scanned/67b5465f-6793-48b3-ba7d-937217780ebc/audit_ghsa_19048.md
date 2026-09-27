# [M] lakeFS affected by unauthenticated access to API usage metrics

## Summary
Severity: Medium
Advisory: GHSA-h238-5mwf-8xw8
CVE: CVE-2025-64179
CWE: CWE-200, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-03
Source: https://github.com/advisories/GHSA-h238-5mwf-8xw8
Type: github-advisory

## Affected
- Go: `github.com/treeverse/lakefs` — affected >=0 <1.71.0

## Details
### Impact

Missing authentication in the `/api/v1/usage-report/summary` endpoint allows anyone to retrieve aggregate API usage counts. While no sensitive data is disclosed, the endpoint may reveal information about service activity or uptime.

### Patches
Upgrade to >v1.70.1

### Workarounds

Any **ONE** of these is sufficient to block this reporting:
- Disable usage reporting by setting configuration option `usage_report.enabled` or environment variable `LAKEFS_USAGE_REPORT_ENABLED` to `false`.
- Using load-balancer or application level firewall - blocking the request route /api/v1/usage-report/summary.

## References
- https://github.com/treeverse/lakeFS/security/advisories/GHSA-h238-5mwf-8xw8
- https://nvd.nist.gov/vuln/detail/CVE-2025-64179
- https://github.com/treeverse/lakeFS/commit/1c8adab852dac2387fcb00a256402b308a610c60
- https://github.com/treeverse/lakeFS
