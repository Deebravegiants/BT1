# [M] Mattermost Jira Plugin does not properly check security levels

## Summary
Severity: Medium
Advisory: GHSA-qr8f-cjw7-838m
CVE: CVE-2024-24774
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-qr8f-cjw7-838m
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-jira` — affected >=0 <4.0.0-rc1

## Details
Mattermost Jira Plugin handling subscriptions fails to check the security level of an incoming issue or limit it based on the user who created the subscription resulting in registered users on Jira being able to create webhooks that give them access to all Jira issues.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24774
- https://github.com/mattermost/mattermost-plugin-jira/commit/5f5e084d169bf6b82d5c46a7a7eb033e1a01c6de
- https://mattermost.com/security-updates
- mattermost/mattermost-plugin-jira
