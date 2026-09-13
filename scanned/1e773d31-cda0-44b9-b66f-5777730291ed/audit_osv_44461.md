# [H] iFlytek astron-agent through 1.1.1 Workflow Hijacking via Missing Ownership Check

## Summary
Severity: High
Advisory: CVE-2026-82475
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82475
Type: osv

## Details
iFlytek astron-agent through 1.1.1 contains an authorization bypass vulnerability in the copyFlow endpoint that fails to validate workflow ownership. Authenticated attackers can enumerate workflow identifiers and overwrite other tenants' workflows or copy private workflows to read their definitions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82475.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82475
- https://www.vulncheck.com/advisories/iflytek-astron-agent-through-1.1.1-workflow-hijacking-via-missing-ownership-check
- https://github.com/iflytek/astron-agent/issues/1590
- https://github.com/iflytek/astron-agent
- https://github.com/iflytek/astron-agent/blob/v1.1.1/console/backend/toolkit/src/main/java/com/iflytek/astron/console/toolkit/service/workflow/WorkflowService.java
