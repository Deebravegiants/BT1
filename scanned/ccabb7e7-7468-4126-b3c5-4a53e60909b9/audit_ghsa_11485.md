# [M] Keycloak: Denial of Service due to excessive SAMLRequest decompression

## Summary
Severity: Medium
Advisory: GHSA-xv6h-r36f-3gp5
CVE: CVE-2026-2575
CWE: CWE-409
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-xv6h-r36f-3gp5
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-saml-adapter-core` — affected >=0 <26.5.4
- Maven: `org.keycloak:keycloak-saml-core` — affected >=0 <26.5.4
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.5.4

## Details
A flaw was found in Keycloak. An unauthenticated remote attacker can trigger an application level Denial of Service (DoS) by sending a highly compressed SAMLRequest through the SAML Redirect Binding. The server fails to enforce size limits during DEFLATE decompression, leading to an OutOfMemoryError (OOM) and subsequent process termination. This vulnerability allows an attacker to disrupt the availability of the service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2575
- https://github.com/keycloak/keycloak/issues/46372
- https://github.com/keycloak/keycloak/commit/4f90ef67f698dfb45df0d2f4981271a7c8b47f04
- https://access.redhat.com/errata/RHSA-2026:3947
- https://access.redhat.com/errata/RHSA-2026:3948
- https://access.redhat.com/security/cve/CVE-2026-2575
- https://bugzilla.redhat.com/show_bug.cgi?id=2440149
- https://github.com/keycloak/keycloak
