# [M] wildfly-core Exposure of Sensitive Information to an Unauthorized Actor vulnerability

## Summary
Severity: Medium
Advisory: GHSA-26qx-4m49-6cfr
CVE: CVE-2023-4061
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-11-08
Source: https://github.com/advisories/GHSA-26qx-4m49-6cfr
Type: github-advisory

## Affected
- Maven: `org.wildfly.core:wildfly-controller` — affected >=0 <22.0.0.Final

## Details
A flaw was found in wildfly-core. A management user could use the resolve-expression in the HAL Interface to read possible sensitive information from the Wildfly system. This issue could allow a malicious user to access the system and obtain possible sensitive information from the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4061
- https://github.com/wildfly/wildfly-core/pull/5703
- https://github.com/wildfly/wildfly-core/commit/25728f370c2e90969854717ba4bb5182727f3f49
- https://access.redhat.com/errata/RHSA-2023:5484
- https://access.redhat.com/errata/RHSA-2023:5485
- https://access.redhat.com/errata/RHSA-2023:5486
- https://access.redhat.com/errata/RHSA-2023:5488
- https://access.redhat.com/security/cve/CVE-2023-4061
- https://bugzilla.redhat.com/show_bug.cgi?id=2228608
- https://github.com/wildfly/wildfly-core
