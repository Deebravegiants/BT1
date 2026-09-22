# [C] Authentication Bypass in tyk-identity-broker

## Summary
Severity: Critical
Advisory: GHSA-599h-8wpj-75xj
CVE: CVE-2021-23365
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-599h-8wpj-75xj
Type: github-advisory

## Affected
- Go: `github.com/tyktechnologies/tyk-identity-broker` — affected >=0 <1.1.1

## Details
The package github.com/tyktechnologies/tyk-identity-broker before 1.1.1 are vulnerable to Authentication Bypass via the Go XML parser which can cause SAML authentication bypass. This is because the XML parser doesn’t guarantee integrity in the XML round-trip (encoding/decoding XML data).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23365
- https://github.com/TykTechnologies/tyk-identity-broker/pull/147
- https://github.com/TykTechnologies/tyk-identity-broker/commit/243092965b0f93a95a14cb882b5b9a3df61dd5c0
- https://github.com/TykTechnologies/tyk-identity-broker/commit/46f70420e0911e4e8b638575e29d394c227c75d0
- https://github.com/TykTechnologies/tyk-identity-broker/releases/tag/v1.1.1
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMTYKTECHNOLOGIESTYKIDENTITYBROKER-1089720
