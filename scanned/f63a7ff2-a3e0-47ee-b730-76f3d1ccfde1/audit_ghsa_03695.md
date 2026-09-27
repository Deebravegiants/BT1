# [M] Forced Logout in keycloak-connect

## Summary
Severity: Medium
Advisory: GHSA-68hw-vfh7-xvg8
CVE: CVE-2019-10157
CWE: CWE-287, CWE-345
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-68hw-vfh7-xvg8
Type: github-advisory

## Affected
- npm: `keycloak-connect` — affected >=0 <4.8.3

## Details
Versions of `keycloak-connect` prior to 4.4.0 are vulnerable to Forced Logout. The package fails to validate JWT signatures on the `/k_logout` route, allowing attackers to logout users and craft malicious JWTs with NBF values that prevent user access indefinitely.


## Recommendation

Upgrade to version 4.4.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10157
- https://github.com/keycloak/keycloak-nodejs-connect/commit/55e54b55d05ba636bc125a8f3d39f0052d13f8f6
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10157
- https://snyk.io/vuln/SNYK-JS-KEYCLOAKNODEJSCONNECT-449920
- https://www.npmjs.com/advisories/978
- http://www.securityfocus.com/bid/108734
