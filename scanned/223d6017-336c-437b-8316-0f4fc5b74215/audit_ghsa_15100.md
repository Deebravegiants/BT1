# [H] Quarkus Improper Handling of Insufficient Permissions or Privileges and Improper Handling of Exceptional Conditions vulnerability

## Summary
Severity: High
Advisory: GHSA-8j3x-w35r-rw4r
CVE: CVE-2023-6267
CWE: CWE-280, CWE-502, CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-01-25
Source: https://github.com/advisories/GHSA-8j3x-w35r-rw4r
Type: github-advisory

## Affected
- Maven: `io.quarkus.resteasy.reactive:resteasy-reactive` — affected >=0 <2.13.9.Final
- Maven: `io.quarkus.resteasy.reactive:resteasy-reactive` — affected >=3.0.0.Final <3.2.9.Final

## Details
A flaw was found in the json payload. If annotation based security is used to secure a REST resource, the JSON body that the resource may consume is being processed (deserialized) prior to the security constraints being evaluated and applied. This does not happen with configuration based security.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6267
- https://access.redhat.com/errata/RHSA-2024:0494
- https://access.redhat.com/errata/RHSA-2024:0495
- https://access.redhat.com/security/cve/CVE-2023-6267
- https://bugzilla.redhat.com/show_bug.cgi?id=2251155
- https://github.com/quarkusio/quarkus
