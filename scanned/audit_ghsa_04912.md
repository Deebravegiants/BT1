# [M] Spring Retry has Cache Exhaustion in Stateful Retries that leads to Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-2827-2mxx-j8pv
CVE: CVE-2026-41710
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-2827-2mxx-j8pv
Type: github-advisory

## Affected
- Maven: `org.springframework.retry:spring-retry` — affected >=2.0.0 <2.0.13
- Maven: `org.springframework.retry:spring-retry` — affected >=0

## Details
An attacker can craft a large number of unique requests that trigger a failure, exhausting the capacity of the application-wide stateful retry cache. Once the cache is full, it permanently rejects any further updates, causing all later stateful retries and circuit breakers in the application to fail.

Affected versions:
Spring Retry 2.0.0 through 2.0.12; 1.3.0 through 1.3.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41710
- https://github.com/spring-attic/spring-retry/issues/505
- https://github.com/spring-attic/spring-retry/commit/6f351edae3d3575fffbde3c0f62fef963dacd152
- https://github.com/spring-attic/spring-retry/releases/tag/v2.0.13
- https://github.com/spring-projects/spring-retry
- https://spring.io/security/cve-2026-41710
