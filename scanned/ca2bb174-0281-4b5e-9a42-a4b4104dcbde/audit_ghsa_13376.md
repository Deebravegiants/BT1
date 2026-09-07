# [M] quarkus-core vulnerable to client driven TLS cipher downgrading

## Summary
Severity: Medium
Advisory: GHSA-3fhx-3vvg-2j84
CVE: CVE-2023-2974
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-04
Source: https://github.com/advisories/GHSA-3fhx-3vvg-2j84
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-core` — affected >=0 <2.16.8.Final

## Details
A vulnerability was found in quarkus-core. This vulnerability occurs because the TLS protocol configured with quarkus.http.ssl.protocols is not enforced, and the client can force the selection of the weaker supported TLS protocol.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2974
- https://github.com/quarkusio/quarkus/pull/34469
- https://github.com/quarkusio/quarkus/commit/468397ae53a8d6aae933d0d406f94965e97d1935
- https://access.redhat.com/errata/RHSA-2023:3809
- https://access.redhat.com/security/cve/CVE-2023-2974
- https://bugzilla.redhat.com/show_bug.cgi?id=2211026
- https://github.com/quarkusio/quarkus
