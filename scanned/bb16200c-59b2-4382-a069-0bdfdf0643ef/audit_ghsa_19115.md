# [H] io.quarkus:quarkus-resteasy: Memory Leak in Quarkus RESTEasy Classic When Client Requests Timeout

## Summary
Severity: High
Advisory: GHSA-4fwr-mh5q-hchh
CVE: CVE-2025-1634
CWE: CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-26
Source: https://github.com/advisories/GHSA-4fwr-mh5q-hchh
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-resteasy` — affected >=3.16.0.CR1 <3.19.1
- Maven: `io.quarkus:quarkus-resteasy` — affected >=3.9.0.CR1 <3.15.3.1
- Maven: `io.quarkus:quarkus-resteasy` — affected >=0 <3.8.6.1

## Details
A flaw was found in the quarkus-resteasy extension, which causes memory leaks when client requests with low timeouts are made. If a client request times out, a buffer is not released correctly, leading to increased memory usage and eventual application crash due to OutOfMemoryError.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1634
- https://github.com/quarkusio/quarkus/issues/46412
- https://github.com/quarkusio/quarkus/pull/46426
- https://github.com/quarkusio/quarkus/pull/46425
- https://github.com/quarkusio/quarkus/pull/46419
- https://github.com/quarkusio/quarkus/commit/80b8eb41678cdccb46e964dc324d048a5ef00f4b
- https://github.com/quarkusio/quarkus/commit/70ffbd00d71d43afa7eade32d6ed586cf927c237
- https://github.com/quarkusio/quarkus/commit/30d949a4c54ba1057738849a804d2329c09e57be
- https://github.com/quarkusio/quarkus/commit/291296befabf659b71acbfc6e03a12bd09a920f8
- https://github.com/quarkusio/quarkus
- https://bugzilla.redhat.com/show_bug.cgi?id=2347319
- https://access.redhat.com/security/cve/CVE-2025-1634
- https://access.redhat.com/errata/RHSA-2025:9922
- https://access.redhat.com/errata/RHSA-2025:23417
- https://access.redhat.com/errata/RHSA-2025:2067
- https://access.redhat.com/errata/RHSA-2025:1885
- https://access.redhat.com/errata/RHSA-2025:1884
- https://access.redhat.com/errata/RHSA-2025:12511
