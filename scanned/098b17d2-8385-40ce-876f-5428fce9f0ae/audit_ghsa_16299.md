# [M] Mattermost allows attackers access to posts in channels they are not a member of

## Summary
Severity: Medium
Advisory: GHSA-hwjf-4667-gqwx
CVE: CVE-2024-1942
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-hwjf-4667-gqwx
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.3.0 <9.3.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.2.0 <9.2.5
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.9

## Details
Mattermost versions 8.1.x before 8.1.9, 9.2.x before 9.2.5, and 9.3.0 fail to sanitize the metadata on posts containing permalinks under specific conditions, which allows an authenticated attacker to access the contents of individual posts in channels they are not a member of.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1942
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
