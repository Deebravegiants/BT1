# [M] Mattermost doesn't validate user channel membership when attaching Mattermost posts as comments to Jira issues

## Summary
Severity: Medium
Advisory: GHSA-fmqf-pmcm-8cx9
CVE: CVE-2025-13767
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-24
Source: https://github.com/advisories/GHSA-fmqf-pmcm-8cx9
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20251121122154-b57c297c6d7
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.8
- Go: `github.com/mattermost/mattermost-server` — affected >=10.12.0 <10.12.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.0.0 <11.0.6
- Go: `github.com/mattermost/mattermost-server` — affected >=11.1.0 <11.1.1

## Details
Mattermost versions 11.1.x <= 11.1.0, 11.0.x <= 11.0.5, 10.12.x <= 10.12.3, 10.11.x <= 10.11.7 fails to validate user channel membership when attaching Mattermost posts as comments to Jira issues, which allows an authenticated attacker with access to the Jira plugin to read post content and attachments from channels they do not have access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13767
- https://github.com/mattermost/mattermost/pull/34551
- https://github.com/mattermost/mattermost/commit/b57c297c6d7ae6812d85e32a625806ac9555deee
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2026-4259
