# [H] One-Click Mattermost Account Takeover via Poisoned RelayState SAML Parameter

## Summary
Severity: High
Advisory: CVE-2025-9072
Aliases: GHSA-69j8-prx2-vx98, GO-2025-3958
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-9072
Type: osv

## Details
Mattermost versions 10.10.x <= 10.10.1, 10.5.x <= 10.5.9, 10.9.x <= 10.9.4 fail to validate the redirect_to parameter, allowing an attacker to craft a malicious link that, once a user authenticates with their SAML provider, could post the user’s cookies to an attacker-controlled URL.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9072.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-9072
