# [M] Keycloak vulnerable to reflected XSS via wildcard in OIDC redirect_uri

## Summary
Severity: Medium
Advisory: GHSA-cvg2-7c3j-g36j
CVE: CVE-2023-6134
CWE: CWE-75
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-cvg2-7c3j-g36j
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <23.0.3

## Details
Keycloak prevents certain schemes in redirects, but permits them if a wildcard is appended to the token. This could permit an attacker to submit a specially crafted request leading to XSS or possibly further attacks.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-cvg2-7c3j-g36j
- https://nvd.nist.gov/vuln/detail/CVE-2023-6134
- https://github.com/keycloak/keycloak/commit/15a21bf8e4fb71f006ba9caf25b9c9d1d152cd20
- https://access.redhat.com/errata/RHSA-2023:7854
- https://access.redhat.com/errata/RHSA-2023:7855
- https://access.redhat.com/errata/RHSA-2023:7856
- https://access.redhat.com/errata/RHSA-2023:7857
- https://access.redhat.com/errata/RHSA-2023:7858
- https://access.redhat.com/errata/RHSA-2023:7860
- https://access.redhat.com/errata/RHSA-2023:7861
- https://access.redhat.com/security/cve/CVE-2023-6134
- https://bugzilla.redhat.com/show_bug.cgi?id=2249673
- https://github.com/keycloak/keycloak
