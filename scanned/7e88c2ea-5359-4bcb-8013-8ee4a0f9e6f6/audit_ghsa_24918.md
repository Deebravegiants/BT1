# [H] Keycloak Improper Bruteforce Detection

## Summary
Severity: High
Advisory: GHSA-85v8-vx4w-q684
CVE: CVE-2018-14657
CWE: CWE-307
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-85v8-vx4w-q684
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <4.6.0.Final

## Details
A flaw was found in Keycloak 4.2.1.Final, 4.3.0.Final. When TOPT enabled, an improper implementation of the Brute Force detection algorithm will not enforce its protection measures.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14657
- https://access.redhat.com/errata/RHSA-2018:3592
- https://access.redhat.com/errata/RHSA-2018:3593
- https://access.redhat.com/errata/RHSA-2018:3595
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14657
- https://github.com/keycloak/keycloak
