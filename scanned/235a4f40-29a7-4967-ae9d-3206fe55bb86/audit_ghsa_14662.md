# [H] io.quarkus.http/quarkus-http-core: Quarkus HTTP Cookie Smuggling

## Summary
Severity: High
Advisory: GHSA-cxrx-q234-m22m
CVE: CVE-2024-12397
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-12-12
Source: https://github.com/advisories/GHSA-cxrx-q234-m22m
Type: github-advisory

## Affected
- Maven: `io.quarkus.http:quarkus-http-core` — affected >=0 <5.3.4

## Details
A flaw was found in Quarkus-HTTP, which incorrectly parses cookies with certain value-delimiting characters in incoming requests. This issue could allow an attacker to construct a cookie value to exfiltrate HttpOnly cookie values or spoof arbitrary additional cookie values, leading to unauthorized data access or modification. The main threat from this flaw impacts data confidentiality and integrity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12397
- https://github.com/quarkusio/quarkus-http/pull/170
- https://github.com/quarkusio/quarkus-http/commit/cfc99d80fce2e3a3dbf06972e648e79e925a7ae7
- https://access.redhat.com/errata/RHSA-2025:0900
- https://access.redhat.com/errata/RHSA-2025:1082
- https://access.redhat.com/errata/RHSA-2025:3018
- https://access.redhat.com/errata/RHSA-2025:8761
- https://access.redhat.com/security/cve/CVE-2024-12397
- https://bugzilla.redhat.com/show_bug.cgi?id=2331298
- https://github.com/quarkusio/quarkus-http
