# [M] Quarkus REST has potential worker thread starvation when HTTP connection is closed while waiting to write

## Summary
Severity: Medium
Advisory: GHSA-5rfx-cp42-p624
CVE: CVE-2025-66560
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-5rfx-cp42-p624
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-rest` — affected >=0 <3.20.5
- Maven: `io.quarkus:quarkus-rest` — affected >=3.21.0 <3.27.2
- Maven: `io.quarkus:quarkus-rest` — affected >=3.30.0 <3.31.0

## Details
A vulnerability exists in the HTTP layer of Quarkus REST related to response handling. When a response is being written, the framework waits for previously written response chunks to be fully transmitted before proceeding. If the client connection is dropped during this waiting period, the associated worker thread is never released and becomes permanently blocked. Under sustained or repeated occurrences, this can exhaust the available worker threads, leading to degraded performance, or complete unavailability of the application.

## Workarounds

For versions without the fix applied, it is recommended to implement a health check that monitors the status and saturation of the worker thread pool. This helps detect abnormal thread retention early and allows operators to take corrective action before the application’s responsiveness is impacted.

## Credits

CVE reported by Shaswata Jash, Nokia

## References
- https://github.com/quarkusio/quarkus/security/advisories/GHSA-5rfx-cp42-p624
- https://nvd.nist.gov/vuln/detail/CVE-2025-66560
- https://github.com/quarkusio/quarkus
