# [M] Zipkin Server vulnerable to Insecure Resource Initialization through its /heapdump endpoint

## Summary
Severity: Medium
Advisory: GHSA-794x-8x6x-qpfc
CVE: CVE-2025-53602
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-04
Source: https://github.com/advisories/GHSA-794x-8x6x-qpfc
Type: github-advisory

## Affected
- Maven: `io.zipkin:zipkin-server` — affected >=0

## Details
Zipkin through 3.5.1 has a /heapdump endpoint (associated with the use of Spring Boot Actuator), a similar issue to CVE-2025-48927.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53602
- https://github.com/openzipkin/zipkin/pull/3804
- https://github.com/openzipkin/zipkin/commit/3c7605dfdfab2dd341cf0ea121a56cefcd580d9e
- https://github.com/openzipkin/zipkin
- https://zipkin.io
