# [M] Mesop: DoS in /hot-reload endpoint allows unauthenticated attacker to exhaust worker threads and crash the server

## Summary
Severity: Medium
Advisory: CVE-2026-77357
Aliases: GHSA-8p72-497j-83mx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-77357
Type: osv

## Details
Mesop is a Python-based UI framework that allows users to build web applications. Prior to 1.3.3, applications running in debug mode expose a GET /hot-reload endpoint whose unbounded loop depends on the user-supplied counter parameter, allowing an unauthenticated attacker to hold worker threads with high counter values until the worker pool is exhausted and the server becomes unavailable. A single unauthenticated attacker can crash the Mesop server with minimal effort. Because the attack leverages worker exhaustion, the server remains unresponsive until it is manually restarted. This issue is fixed in version 1.3.3.

## References
- https://github.com/mesop-dev/mesop/releases/tag/v1.3.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77357.json
- https://github.com/mesop-dev/mesop/security/advisories/GHSA-8p72-497j-83mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-77357
- https://github.com/mesop-dev/mesop/commit/2b8e7f2c349c9e2eec202f46b07bada83061ce2d
