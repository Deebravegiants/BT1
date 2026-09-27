# [M] Mattermost webapp crash via a crafted post

## Summary
Severity: Medium
Advisory: GHSA-w6xh-c82w-h997
CVE: CVE-2025-20621
CWE: CWE-1287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-16
Source: https://github.com/advisories/GHSA-w6xh-c82w-h997
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.2.0 <10.2.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.1.0 <10.1.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.0.0 <10.0.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20241127161322-25ff7a3779a5

## Details
Mattermost versions 10.2.x <= 10.2.0, 9.11.x <= 9.11.5, 10.0.x <= 10.0.3, 10.1.x <= 10.1.3 fail to properly handle posts with attachments containing fields that cannot be cast to a String, which allows an attacker to cause the webapp to crash via creating and sending such a post to a channel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-20621
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
