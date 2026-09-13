# [H] Keycloak Build Process Exposes Sensitive Data

## Summary
Severity: High
Advisory: GHSA-v7gv-xpgf-6395
CVE: CVE-2024-10451
CWE: CWE-798
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-v7gv-xpgf-6395
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=0 <24.0.9
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=25.0.0 <26.0.6

## Details
A flaw was found in Keycloak. This issue occurs because sensitive runtime values, such as passwords, may be captured during the Keycloak build process and embedded as default values in bytecode, leading to unintended information disclosure. In Keycloak 26, sensitive data specified directly in environment variables during the build process is also stored as a default values, making it accessible during runtime. Indirect usage of environment variables for SPI options and Quarkus properties is also vulnerable due to unconditional expansion by PropertyMapper logic, capturing sensitive data as default values in all Keycloak versions up to 26.0.2.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-v7gv-xpgf-6395
- https://nvd.nist.gov/vuln/detail/CVE-2024-10451
- https://github.com/keycloak/keycloak/commit/198214310eb45b86707f823ccb5a2d65c814b528
- https://access.redhat.com/errata/RHSA-2024:10175
- https://access.redhat.com/errata/RHSA-2024:10176
- https://access.redhat.com/errata/RHSA-2024:10177
- https://access.redhat.com/errata/RHSA-2024:10178
- https://access.redhat.com/security/cve/CVE-2024-10451
- https://bugzilla.redhat.com/show_bug.cgi?id=2322096
- https://github.com/keycloak/keycloak
