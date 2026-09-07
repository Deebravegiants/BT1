# [M] XSS in Keycloak

## Summary
Severity: Medium
Advisory: GHSA-8vf3-4w62-m3pq
CVE: CVE-2020-1697
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-04-15
Source: https://github.com/advisories/GHSA-8vf3-4w62-m3pq
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <9.0.0

## Details
It was found in all keycloak versions before 9.0.0 that links to external applications (Application Links) in the admin console are not validated properly and could allow Stored XSS attacks. An authed malicious user could create URLs to trick users in other realms, and possibly conduct further attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1697
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1697
