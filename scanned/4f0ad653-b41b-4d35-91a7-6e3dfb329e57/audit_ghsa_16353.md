# [M] Use of Insufficiently Random Values in github.com/greenpau/caddy-security

## Summary
Severity: Medium
Advisory: GHSA-c7vf-m394-m4x4
CVE: CVE-2024-21495
CWE: CWE-330
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-17
Source: https://github.com/advisories/GHSA-c7vf-m394-m4x4
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
Versions of the package github.com/greenpau/caddy-security before 1.0.42 are vulnerable to Insecure Randomness due to using an insecure random number generation library which could possibly be predicted via a brute-force search. Attackers could use the potentially predictable nonce value used for authentication purposes in the OAuth flow to conduct OAuth replay attacks. In addition, insecure randomness is used while generating multifactor authentication (MFA) secrets and creating API keys in the database package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21495
- https://github.com/greenpau/caddy-security/issues/265
- https://github.com/greenpau/go-authcrunch/commit/ecd3725baf2683eb1519bb3c81ae41085fbf7dc2
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGREENPAUCADDYSECURITY-6248275
- github.com/greenpau/caddy-security
