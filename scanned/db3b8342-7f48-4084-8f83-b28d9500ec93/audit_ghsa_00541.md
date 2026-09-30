# [H] Improper Authentication in org.keycloak:keycloak-core

## Summary
Severity: High
Advisory: GHSA-95m6-mjh3-58gm
CVE: CVE-2016-8609
CWE: CWE-287, CWE-384
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-95m6-mjh3-58gm
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <2.3.0

## Details
It was found that the keycloak before 2.3.0 did not implement authentication flow correctly. An attacker could use this flaw to construct a phishing URL, from which he could hijack the user's session. This could lead to information disclosure, or permit further possible attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8609
- https://github.com/advisories/GHSA-95m6-mjh3-58gm
