# [M] Kestra: Unauthenticated management/actuator endpoints exposed on port 8081 (/env, /loggers) bypass API basic-auth

## Summary
Severity: Medium
Advisory: CVE-2026-73245
Aliases: GHSA-hpj9-grjp-7vc7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73245
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to 2.0.0-rc6, Kestra's cli/src/main/resources/application.yml serves Micronaut management endpoints on port 8081 without authentication even when Basic Auth protects /api/v1/** on port 8080, allowing unauthenticated GET /env requests to disclose resolved configuration and POST /loggers/{name} requests to change runtime log levels. This issue is fixed in 2.0.0-rc6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73245.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-hpj9-grjp-7vc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-73245
