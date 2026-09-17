# [H] Micrometer HTTP server instrumentations DoS

## Summary
Severity: High
Advisory: GHSA-g3pr-3p32-fp23
CVE: CVE-2026-40984
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-g3pr-3p32-fp23
Type: github-advisory

## Affected
- Maven: `io.micrometer:micrometer-core` — affected >=1.16.0 <1.16.6
- Maven: `io.micrometer:micrometer-core` — affected >=1.15.0 <1.15.12
- Maven: `io.micrometer:micrometer-core` — affected >=1.14.0
- Maven: `io.micrometer:micrometer-core` — affected >=1.10.0
- Maven: `io.micrometer:micrometer-core` — affected >=0
- Maven: `io.micrometer:micrometer-jetty12` — affected >=1.16.0 <1.16.6
- Maven: `io.micrometer:micrometer-jetty12` — affected >=1.15.0 <1.15.12
- Maven: `io.micrometer:micrometer-jetty12` — affected >=1.14.0
- Maven: `io.micrometer:micrometer-jetty12` — affected >=0
- Maven: `io.micrometer:micrometer-jetty11` — affected >=1.16.0 <1.16.6
- Maven: `io.micrometer:micrometer-jetty11` — affected >=1.15.0 <1.15.12
- Maven: `io.micrometer:micrometer-jetty11` — affected >=1.14.0
- Maven: `io.micrometer:micrometer-jetty11` — affected >=0

## Details
In Micrometer, it is possible for a user to provide specially crafted HTTP requests that may cause a denial-of-service (DoS) condition.

Affected versions:
micrometer-core 1.16.0 through 1.16.5; 1.15.0 through 1.15.11; 1.14.0 through 1.14.15; 1.13.0 through 1.13.18; 1.9.0 through 1.9.17.
micrometer-jetty11 1.16.0 through 1.16.5; 1.15.0 through 1.15.11; 1.14.0 through 1.14.15; 1.13.0 through 1.13.18.
micrometer-jetty12 1.16.0 through 1.16.5; 1.15.0 through 1.15.11; 1.14.0 through 1.14.15; 1.13.0 through 1.13.18.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40984
- https://github.com/micrometer-metrics/micrometer/commit/36da131525228188a36779a28471a76c79213dd4
- https://access.redhat.com/errata/RHSA-2026:36839
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/errata/RHSA-2026:41951
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/errata/RHSA-2026:54435
- https://access.redhat.com/errata/RHSA-2026:62260
- https://access.redhat.com/security/cve/CVE-2026-40984
- https://bugzilla.redhat.com/show_bug.cgi?id=2486716
- https://github.com/micrometer-metrics/micrometer
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40984.json
- https://spring.io/security/cve-2026-40984
