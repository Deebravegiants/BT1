# [H] Keycloak's admin API allows low privilege users to use administrative functions

## Summary
Severity: High
Advisory: GHSA-2cww-fgmg-4jqc
CVE: CVE-2024-3656
CWE: CWE-200, CWE-269, CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-06-11
Source: https://github.com/advisories/GHSA-2cww-fgmg-4jqc
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <24.0.5

## Details
Users with low privileges (just plain users in the realm) are able to utilize administrative functionalities within Keycloak admin interface. This issue presents a significant security risk as it allows unauthorized users to perform actions reserved for administrators, potentially leading to data breaches or system compromise.

**Acknowledgements:**
Special thanks to Maurizio Agazzini for reporting this issue and helping us improve our project.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-2cww-fgmg-4jqc
- https://nvd.nist.gov/vuln/detail/CVE-2024-3656
- https://github.com/keycloak/keycloak/commit/d9f0c84b797525eac55914db5f81a8133ef5f9b1
- https://access.redhat.com/errata/RHSA-2024:3572
- https://access.redhat.com/errata/RHSA-2024:3575
- https://access.redhat.com/security/cve/CVE-2024-3656
- https://bugzilla.redhat.com/show_bug.cgi?id=2274403
- https://github.com/advisories/GHSA-2cww-fgmg-4jqc
- https://github.com/hnsecurity/vulns/blob/main/HNS-2024-08-Keycloak.md
- https://github.com/keycloak/keycloak
- https://news.ycombinator.com/item?id=42136000
- https://security.humanativaspa.it/an-analysis-of-the-keycloak-authentication-system
