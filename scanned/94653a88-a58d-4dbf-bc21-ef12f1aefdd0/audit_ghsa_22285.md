# [M] Mattermost Server is vulnerable to channel invisibility DoS via misformatted post

## Summary
Severity: Medium
Advisory: GHSA-x6mw-hf2j-vqpc
CVE: CVE-2017-18873
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x6mw-hf2j-vqpc
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2-0.20171013141717-ee57a5829ab1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0 <4.2.1-0.20171013140502-b3e4b0ac9168
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. It allows attackers to cause a denial of service (channel invisibility) via a misformated post.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18873
- https://github.com/mattermost/mattermost/commit/9adaf53e110e0e806b21903111aacb93129668cb
- https://github.com/mattermost/mattermost/commit/b3e4b0ac91682093276a653f7ccd5774aaa9cd06
- https://github.com/mattermost/mattermost/commit/ee57a5829ab162859e0e355dac6cfe6ca1a8f379
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
