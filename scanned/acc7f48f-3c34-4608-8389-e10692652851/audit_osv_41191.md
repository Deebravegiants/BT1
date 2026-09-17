# [M] RuoYi-Vue-Plus - Missing Authorization on Workflow Task Management Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-58176
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58176
Type: osv

## Details
RuoYi-Vue-Plus through 5.6.2, fixed in commit 88d03d9, exposes workflow task management endpoints under /workflow/task (FlwTaskController) without any permission check: the controller declares no class-level or method-level authorization annotation, so the endpoints are gated only by global authentication. Any authenticated user, regardless of assigned role, can therefore reassign workflow approval tasks to arbitrary users via updateAssignee (defeating segregation of duties in the approval process), urge arbitrary tasks, and enumerate all pending and finished tasks via the pageByAllTaskWait and pageByAllTaskFinish listing endpoints. The issue was resolved by adding permission identifiers (SaCheckPermission) to these endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58176.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58176
- https://www.vulncheck.com/advisories/ruoyi-vue-plus-missing-authorization-on-workflow-task-management-endpoints
- https://github.com/dromara/RuoYi-Vue-Plus/commit/88d03d970d4d1e96e4fb2dfefaf19f627e8673e9
- https://github.com/dromara/RuoYi-Vue-Plus
- https://github.com/dromara/RuoYi-Vue-Plus/issues/44
