# [H] Kestra: Unauthenticated management `/worker` endpoint exposes live task configuration and plaintext credentials

## Summary
Severity: High
Advisory: CVE-2026-73246
Aliases: GHSA-m65f-q5gj-hg46
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73246
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to 2.0.0-rc6, Kestra's worker/src/main/java/io/kestra/worker/endpoint/WorkerEndpoint.java serves GET /worker without authentication and serializes the complete live Task object, which can expose commands, environment variables, HTTP headers, connection details, plaintext credentials, and execution identifiers while the main API on port 8080 remains protected. This issue is fixed in 2.0.0-rc6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73246.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-m65f-q5gj-hg46
- https://nvd.nist.gov/vuln/detail/CVE-2026-73246
