# [M] Keycloak Missing authentication for critical function

## Summary
Severity: Medium
Advisory: GHSA-xf46-8vvp-4hxx
CVE: CVE-2021-20262
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-12
Source: https://github.com/advisories/GHSA-xf46-8vvp-4hxx
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0

## Details
A flaw was found in Keycloak 12.0.0 where re-authentication does not occur while updating the password. This flaw allows an attacker to take over an account if they can obtain temporary, physical access to a user’s browser. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20262
- https://bugzilla.redhat.com/show_bug.cgi?id=1933639
