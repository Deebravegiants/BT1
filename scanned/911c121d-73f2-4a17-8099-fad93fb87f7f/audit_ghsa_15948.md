# [M] Keycloak has Vulnerable Redirect URI Validation Results in Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-w8gr-xwp4-r9f7
CVE: CVE-2024-8883
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-w8gr-xwp4-r9f7
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <22.0.13
- Maven: `org.keycloak:keycloak-services` — affected >=23.0.0 <24.0.8
- Maven: `org.keycloak:keycloak-services` — affected >=25.0.0 <25.0.6

## Details
A misconfiguration flaw was found in Keycloak. This issue can allow an attacker to redirect users to an arbitrary URL if a 'Valid Redirect URI' is set to http://localhost/ or http://127.0.0.1/, enabling sensitive information such as authorization codes to be exposed to the attacker, potentially leading to session hijacking.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-w8gr-xwp4-r9f7
- https://nvd.nist.gov/vuln/detail/CVE-2024-8883
- https://github.com/keycloak/keycloak/releases/tag/25.0.6
- https://github.com/keycloak/keycloak/blob/main/services/src/main/java/org/keycloak/protocol/oidc/utils/RedirectUtils.java
- https://github.com/keycloak/keycloak
- https://bugzilla.redhat.com/show_bug.cgi?id=2312511
- https://access.redhat.com/security/cve/CVE-2024-8883
- https://access.redhat.com/errata/RHSA-2024:8826
- https://access.redhat.com/errata/RHSA-2024:8824
- https://access.redhat.com/errata/RHSA-2024:8823
- https://access.redhat.com/errata/RHSA-2024:6890
- https://access.redhat.com/errata/RHSA-2024:6889
- https://access.redhat.com/errata/RHSA-2024:6888
- https://access.redhat.com/errata/RHSA-2024:6887
- https://access.redhat.com/errata/RHSA-2024:6886
- https://access.redhat.com/errata/RHSA-2024:6882
- https://access.redhat.com/errata/RHSA-2024:6880
- https://access.redhat.com/errata/RHSA-2024:6879
- https://access.redhat.com/errata/RHSA-2024:6878
- https://access.redhat.com/errata/RHSA-2024:10386
