# [C] keycloak-connect and keycloak-js improperly handle invalid tokens

## Summary
Severity: Critical
Advisory: GHSA-mw35-24gh-f82w
CVE: CVE-2017-7474
CWE: CWE-253
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-11-15
Source: https://github.com/advisories/GHSA-mw35-24gh-f82w
Type: github-advisory

## Affected
- npm: `keycloak-connect` — affected >=2.5.0 <3.1.0
- npm: `keycloak-js` — affected >=2.5.0 <3.1.0

## Details
It was found that the Keycloak Node.js adapter 2.5 - 3.0 did not handle invalid tokens correctly.  An attacker could use this flaw to bypass authentication and gain access to restricted information, or to possibly conduct further attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7474
- https://bugzilla.redhat.com/show_bug.cgi?id=1445271
- http://rhn.redhat.com/errata/RHSA-2017-1203.html
