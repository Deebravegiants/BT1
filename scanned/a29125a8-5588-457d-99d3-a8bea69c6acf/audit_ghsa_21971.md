# [M] Improper Certificate Validation and Improper Validation of Certificate with Host Mismatch in Keycloak

## Summary
Severity: Medium
Advisory: GHSA-c597-f74m-jgc2
CVE: CVE-2020-1758
CWE: CWE-295, CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-c597-f74m-jgc2
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <10.0.0

## Details
A flaw was found in Keycloak in versions before 10.0.0, where it does not perform the TLS hostname verification while sending emails using the SMTP server. This flaw allows an attacker to perform a man-in-the-middle (MITM) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1758
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1758
- https://issues.redhat.com/browse/KEYCLOAK-13285
