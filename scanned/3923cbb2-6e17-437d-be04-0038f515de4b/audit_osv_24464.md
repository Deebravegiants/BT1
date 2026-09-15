# [M] Oauth authorization codes do not expire when deauthorizing an oauth2 app

## Summary
Severity: Medium
Advisory: CVE-2023-2193
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2023-2193
Type: osv

## Details
Mattermost fails to invalidate existing authorization codes when deauthorizing an OAuth2 app, allowing an attacker possessing an authorization code to generate an access token.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2193.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2193
