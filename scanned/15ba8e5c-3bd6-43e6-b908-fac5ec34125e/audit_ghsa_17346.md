# [H] Mattermost with Jira plugin enabled has Incorrect Implementation of Authentication Algorithm

## Summary
Severity: High
Advisory: GHSA-qvmc-92vg-6r35
CVE: CVE-2025-14273
CWE: CWE-303
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2025-12-22
Source: https://github.com/advisories/GHSA-qvmc-92vg-6r35
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20251121122154-b57c297c6d7a
- Go: `github.com/mattermost/mattermost-plugin-jira` — affected >=0 <4.4.1

## Details
Mattermost versions 11.1.x <= 11.1.0, 11.0.x <= 11.0.5, 10.12.x <= 10.12.3, 10.11.x <= 10.11.7 with the Jira plugin enabled and Mattermost Jira plugin versions <=4.4.0 fail to enforce authentication and issue-key path restrictions in the Jira plugin, which allows an unauthenticated attacker who knows a valid user ID to issue authenticated GET and POST requests to the Jira server via crafted plugin payloads that spoof the user ID and inject arbitrary issue key paths. Mattermost Advisory ID: MMSA-2025-00555

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14273
- https://github.com/mattermost/mattermost-plugin-jira/commit/bf9a1b7e81eb83304056b397c6abab3b062e14a2
- https://github.com/mattermost/mattermost/commit/317025c411ec8c34381fdd4f137a17c63895a4f2
- https://github.com/mattermost/mattermost/commit/463e0d0d3930782d3c975da26c991dcbfccd751c
- https://github.com/mattermost/mattermost/commit/7c36acb68ce3c69defaea540623f794c84ecba93
- https://github.com/mattermost/mattermost/commit/92b1e705225d97ce54d9f720f2e7aa66dc2a086b
- https://github.com/mattermost/mattermost/commit/b57c297c6d7ae6812d85e32a625806ac9555deee
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
