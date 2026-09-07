# [C] Critical severity vulnerability that affects Auth0-WCF-Service-JWT

## Summary
Severity: Critical
Advisory: GHSA-qpvx-gpqm-g98j
CVE: CVE-2019-7644
CWE: CWE-209
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-18
Source: https://github.com/advisories/GHSA-qpvx-gpqm-g98j
Type: github-advisory

## Affected
- NuGet: `Auth0-WCF-Service-JWT` — affected >=0 <1.0.4

## Details
Auth0 Auth0-WCF-Service-JWT before 1.0.4 leaks the expected JWT signature in an error message when it cannot successfully validate the JWT signature. If this error message is presented to an attacker, they can forge an arbitrary JWT token that will be accepted by the vulnerable application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7644
- https://auth0.com/docs/security/bulletins/cve-2019-7644
- https://github.com/advisories/GHSA-qpvx-gpqm-g98j
