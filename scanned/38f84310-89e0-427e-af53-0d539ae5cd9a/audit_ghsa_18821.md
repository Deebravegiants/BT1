# [M] Keycloak Potential Variable Reference in Model Storage Services

## Summary
Severity: Medium
Advisory: GHSA-8hxp-qmph-w5gq
CVE: CVE-2025-9162
CWE: CWE-526
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-8hxp-qmph-w5gq
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-model-storage-services` — affected >=0
- Maven: `org.keycloak:keycloak-model-storage-services` — affected >=26.3.0 <26.3.4

## Details
A flaw was found in org.keycloak/keycloak-model-storage-service. The `KeycloakRealmImport` custom resource substitutes placeholders within imported realm documents, potentially referencing environment variables. This substitution process allows for injection attacks when crafted realm documents are processed. An attacker can leverage this to inject malicious content during the realm import procedure. This can lead to unintended consequences within the Keycloak environment.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-8hxp-qmph-w5gq
- https://access.redhat.com/errata/RHSA-2025:15336
- https://access.redhat.com/errata/RHSA-2025:15337
- https://access.redhat.com/errata/RHSA-2025:15338
- https://access.redhat.com/errata/RHSA-2025:15339
- https://access.redhat.com/errata/RHSA-2025:16399
- https://access.redhat.com/errata/RHSA-2025:16400
- https://access.redhat.com/security/cve/CVE-2025-9162
- https://bugzilla.redhat.com/show_bug.cgi?id=2389396
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/blob/26.3.3/model/storage-services/src/main/java/org/keycloak/exportimport/AbstractFileBasedImportProvider.java#L36
- https://github.com/keycloak/keycloak/blob/75afda410495a9576e00edc3277ab42ca155f806/model/storage-services/src/main/java/org/keycloak/exportimport/AbstractFileBasedImportProvider.java#L35
