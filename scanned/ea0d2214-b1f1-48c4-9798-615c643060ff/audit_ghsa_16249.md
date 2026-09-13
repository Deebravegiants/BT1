# [M] Mattermost vulnerable to denial of service via large number of emoji reactions

## Summary
Severity: Medium
Advisory: GHSA-32h7-7j94-8fc2
CVE: CVE-2024-1402
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-32h7-7j94-8fc2
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.2.0 <9.2.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.1.0 <9.1.5

## Details
Mattermost fails to check if a custom emoji reaction exists when sending it to a post and to limit the amount of custom emojis allowed to be added in a post, allowing an attacker sending a huge amount of non-existent custom emojis in a post to crash the mobile app of a user seeing the post. Fetching posts with huge amounts of reactions results in Uncontrolled Resource Consumption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1402
- https://github.com/mattermost/mattermost/commit/64cb0ca8af2dbda1afcddd1604460591a4799b81
- https://github.com/mattermost/mattermost/commit/6d2440de9fd774b67e65e3aac4ab8b6ef9aba2d8
- https://github.com/mattermost/mattermost/commit/81190e2da128a6985914ea7023a69ac400513fc4
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
