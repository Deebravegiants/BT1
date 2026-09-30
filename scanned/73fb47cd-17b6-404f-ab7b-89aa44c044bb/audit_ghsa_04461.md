# [H] Micrometer gRPC server instrumentation DoS

## Summary
Severity: High
Advisory: GHSA-w737-wx49-qj23
CVE: CVE-2026-40983
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-w737-wx49-qj23
Type: github-advisory

## Affected
- Maven: `io.micrometer:micrometer-core` — affected >=1.16.0 <1.16.6
- Maven: `io.micrometer:micrometer-core` — affected >=1.15.0 <1.15.12

## Details
In Micrometer, it is possible for a user to provide specially crafted gRPC requests that may cause a denial-of-service (DoS) condition.

Affected versions:
Micrometer 1.16.0 through 1.16.5; 1.15.0 through 1.15.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40983
- https://access.redhat.com/errata/RHSA-2026:36839
- https://access.redhat.com/errata/RHSA-2026:41951
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/errata/RHSA-2026:54435
- https://access.redhat.com/errata/RHSA-2026:62260
- https://access.redhat.com/security/cve/CVE-2026-40983
- https://bugzilla.redhat.com/show_bug.cgi?id=2486697
- https://github.com/micrometer-metrics/micrometer
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40983.json
- https://spring.io/security/cve-2026-40983
