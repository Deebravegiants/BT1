# [M] Spring gRPC SecurityContext leaks across requests upon authorization failure

## Summary
Severity: Medium
Advisory: GHSA-4g9c-3x4p-mfpp
CVE: CVE-2026-40968
CWE: CWE-653
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-4g9c-3x4p-mfpp
Type: github-advisory

## Affected
- Maven: `org.springframework.grpc:spring-grpc` — affected >=0 <1.0.3

## Details
When an authenticated user is denied access to a gRPC method, their authenticated identity remains bound to the gRPC worker thread and can be inherited by a subsequent unauthenticated request on the same thread. This may allow the subsequent user to gain escalated permissions.

Affected versions:
Spring gRPC: 1.0.0 - 1.0.2 (fixed in 1.0.3). Older, unsupported versions are also affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40968
- https://github.com/spring-projects/spring-grpc
- https://spring.io/security/cve-2026-40968
