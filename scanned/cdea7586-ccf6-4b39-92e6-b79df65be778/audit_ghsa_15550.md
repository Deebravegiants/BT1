# [M] Eclipse Dataspace Components's ConsumerPullTransferTokenValidationApiController doesn't check for token validit

## Summary
Severity: Medium
Advisory: GHSA-8259-2x72-2gvc
CVE: CVE-2024-8642
CWE: CWE-287, CWE-303
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-09-11
Source: https://github.com/advisories/GHSA-8259-2x72-2gvc
Type: github-advisory

## Affected
- Maven: `org.eclipse.edc:transfer-data-plane` — affected >=0.5.0 <0.9.0

## Details
In Eclipse Dataspace Components, from version 0.5.0 and before version 0.9.0, the ConsumerPullTransferTokenValidationApiController does not check for token validity (expiry, not-before, issuance date), which can allow an attacker to bypass the check for token expiration. The issue requires to have a dataplane configured to support http proxy consumer pull AND include the module "transfer-data-plane". The affected code was marked deprecated from the version 0.6.0 in favour of Dataplane Signaling. In 0.9.0 the vulnerable code has been removed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8642
- https://github.com/eclipse-edc/Connector/commit/04899e91dcdb4a407db4eb7af3e7b6ff9a9e9ad6
- https://github.com/eclipse-edc/Connector
- https://github.com/eclipse-edc/Connector/blob/bcb2e42aee82ce1863be3dcbdab29919d39a0e97/extensions/control-plane/transfer/transfer-data-plane/src/main/java/org/eclipse/edc/connector/controlplane/transfer/dataplane/api/ConsumerPullTransferTokenValidationApiController.java
- https://github.com/eclipse-edc/Connector/releases/tag/v0.9.0
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/28
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/234
