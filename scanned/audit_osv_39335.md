# [H] Heym < 0.0.21 Authorization Bypass in Workflow Execution

## Summary
Severity: High
Advisory: CVE-2026-45226
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-45226
Type: osv

## Details
Heym before 0.0.21 contains an authorization bypass vulnerability in workflow execution that allows authenticated users to execute arbitrary workflows by referencing victim workflow UUIDs without proper access validation. Attackers can create workflows with execute nodes or agent subWorkflowIds pointing to victim workflow UUIDs to load and execute those workflows under attacker-controlled execution paths, exposing victim workflow outputs and triggering workflow nodes with unintended side effects.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45226.json
- https://github.com/heymrun/heym/releases/tag/v0.0.21
- https://nvd.nist.gov/vuln/detail/CVE-2026-45226
- https://www.vulncheck.com/advisories/heym-authorization-bypass-in-workflow-execution
- https://github.com/heymrun/heym/pull/93
- https://github.com/heymrun/heym/commit/3ae3ef6a7d3609da0e910f9ed6b81e99a1661ac8
- https://github.com/heymrun/heym
