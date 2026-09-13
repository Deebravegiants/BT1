# [M] Frappe: Unauthenticated Workflow approval via confirm_action

## Summary
Severity: Medium
Advisory: CVE-2026-63654
Aliases: GHSA-cgwf-xgph-hxgm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63654
Type: osv

## Details
Frappe is a full-stack web application framework. In version 16.31.0 and earlier, the whitelisted frappe.model.workflow.bulk_workflow_approval endpoint in frappe/model/workflow.py accepts safe HTTP methods for state-changing workflow approvals because the endpoint is not restricted to POST. An attacker can induce an authenticated victim browser to submit an approval action with the victim privileges. No released fixed version is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63654.json
- https://github.com/frappe/frappe/security/advisories/GHSA-cgwf-xgph-hxgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-63654
- https://github.com/frappe/frappe/commit/8465376ad9f81775c20892338f920c695b88fb1f
- https://github.com/frappe/frappe/pull/41361
