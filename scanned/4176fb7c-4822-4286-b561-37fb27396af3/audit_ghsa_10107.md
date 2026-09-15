# [M] OpenViking contains a missing authorization vulnerability in the task polling endpoints

## Summary
Severity: Medium
Advisory: GHSA-h336-2wxm-pr6q
CVE: CVE-2026-22680
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-h336-2wxm-pr6q
Type: github-advisory

## Affected
- PyPI: `OpenViking` — affected >=0 <0.3.3

## Details
OpenViking versions prior to 0.3.3 contain a missing authorization vulnerability in the task polling endpoints that allows unauthorized attackers to enumerate or retrieve background task metadata created by other users. Attackers can access the /api/v1/tasks and /api/v1/tasks/{task_id} routes without authentication to expose task type, task status, resource identifiers, archive URIs, result payloads, and error information, potentially causing cross-tenant interference in multi-tenant deployments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22680
- https://github.com/volcengine/OpenViking/pull/1182
- https://github.com/volcengine/OpenViking/commit/8c1c3f3608364ee0bb0e45f73478771a68aebdf5
- https://github.com/volcengine/OpenViking
- https://github.com/volcengine/OpenViking/releases/tag/v0.3.3
- https://www.vulncheck.com/advisories/openviking-missing-authorization-via-task-polling
