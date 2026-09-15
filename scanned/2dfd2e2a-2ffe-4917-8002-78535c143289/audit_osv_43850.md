# [M] Determined Missing Authorization Check on Generic Task Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-75109
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75109
Type: osv

## Details
Determined fails to authorize requests on the generic task kill, pause, and unpause endpoints in the API handlers. Authenticated attackers can disrupt other users' workloads by terminating, pausing, or unpausing tasks they do not own.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75109.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75109
- https://www.vulncheck.com/advisories/determined-missing-authorization-check-on-generic-task-endpoints
- https://github.com/determined-ai/determined/issues/10270
- https://github.com/determined-ai/determined
- https://github.com/determined-ai/determined/blob/main/master/internal/api_generic_tasks.go
