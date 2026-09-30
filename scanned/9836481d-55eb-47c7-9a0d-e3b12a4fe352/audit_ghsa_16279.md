# [M] Improper Restriction of Excessive Authentication Attempts in github.com/greenpau/caddy-security

## Summary
Severity: Medium
Advisory: GHSA-vfph-hjfv-cpv2
CVE: CVE-2024-21500
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-17
Source: https://github.com/advisories/GHSA-vfph-hjfv-cpv2
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
All versions of the package github.com/greenpau/caddy-security are vulnerable to Improper Restriction of Excessive Authentication Attempts via the two-factor authentication (2FA). Although the application blocks the user after several failed attempts to provide 2FA codes, attackers can bypass this blocking mechanism by automating the application’s full multistep 2FA process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21500
- https://github.com/greenpau/caddy-security/issues/271
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGREENPAUCADDYSECURITY-6249864
- github.com/greenpau/caddy-security
