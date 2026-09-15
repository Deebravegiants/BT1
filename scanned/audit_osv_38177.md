# [C] OneUptime: Unauthenticated Workflow Execution via ManualAPI

## Summary
Severity: Critical
Advisory: CVE-2026-35053
Aliases: GHSA-6c3w-7xg4-4cf7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-35053
Type: osv

## Details
OneUptime is an open-source monitoring and observability platform. Prior to version 10.0.42, the Worker service's ManualAPI exposes workflow execution endpoints (GET /workflow/manual/run/:workflowId and POST /workflow/manual/run/:workflowId) without any authentication middleware. An attacker who can obtain or guess a workflow ID can trigger arbitrary workflow execution with attacker-controlled input data, enabling JavaScript code execution, notification abuse, and data manipulation. This issue has been patched in version 10.0.42.

## References
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35053.json
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-6c3w-7xg4-4cf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35053
