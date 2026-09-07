# [M] Cross-site Scripting in Quarkus

## Summary
Severity: Medium
Advisory: GHSA-c57v-hc7m-8px2
CVE: CVE-2023-0044
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-23
Source: https://github.com/advisories/GHSA-c57v-hc7m-8px2
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=0 <2.13.7.Final

## Details
If the Quarkus Form Authentication session cookie Path attribute is set to `/` then a cross-site attack may be initiated which might lead to the Information Disclosure. This attack can be prevented with the Quarkus CSRF Prevention feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0044
- https://access.redhat.com/security/cve/CVE-2023-0044
- https://bugzilla.redhat.com/show_bug.cgi?id=2158081
- https://github.com/quarkusio/quarkus
