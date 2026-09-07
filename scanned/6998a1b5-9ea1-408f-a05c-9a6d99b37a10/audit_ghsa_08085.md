# [M] Mattermost doesn't validate user permissions when creating Jira issues from Mattermost posts

## Summary
Severity: Medium
Advisory: GHSA-9pj7-jh2r-87g8
CVE: CVE-2026-22892
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-9pj7-jh2r-87g8
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0 <11.2.2
- Go: `github.com/mattermost/mattermost-server` — affected >=11.1.0 <11.1.3
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.10

## Details
Mattermost versions 11.1.x <= 11.1.2, 10.11.x <= 10.11.9, 11.2.x <= 11.2.1 fail to validate user permissions when creating Jira issues from Mattermost posts, which allows an authenticated attacker with access to the Jira plugin to read post content and attachments from channels they do not have access to via the /create-issue API endpoint by providing the post ID of an inaccessible post.. Mattermost Advisory ID: MMSA-2025-00550

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22892
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
