# [H] Auth0 Passport-SharePoint does not validate JWT signature

## Summary
Severity: High
Advisory: GHSA-45fh-g845-pj9w
CVE: CVE-2019-13483
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-45fh-g845-pj9w
Type: github-advisory

## Affected
- npm: `passport-sharepoint` — affected >=0 <0.4.0

## Details
Auth0 Passport-SharePoint before 0.4.0 does not validate the JWT signature of an Access Token before processing. This allows attackers to forge tokens and bypass authentication and authorization mechanisms.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13483
- https://auth0.com/docs/security/bulletins/cve-2019-13483
- https://github.com/auth0/passport-sharepoint
