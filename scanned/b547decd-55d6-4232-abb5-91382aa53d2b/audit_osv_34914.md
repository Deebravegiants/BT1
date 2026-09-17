# [M] CVE-2025-66435

## Summary
Severity: Medium
Advisory: CVE-2025-66435
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-66435
Type: osv

## Details
An SSTI (Server-Side Template Injection) vulnerability exists in the get_contract_template method of Frappe ERPNext through 15.89.0. The function renders attacker-controlled Jinja2 templates (contract_terms) using frappe.render_template() with a user-supplied context (doc). Although Frappe uses a custom SandboxedEnvironment, several dangerous globals such as frappe.db.sql are still available in the execution context via get_safe_globals(). An authenticated attacker with access to create or modify a Contract Template can inject arbitrary Jinja expressions into the contract_terms field, resulting in server-side code execution within a restricted but still unsafe context. This vulnerability can be used to leak database information.

## References
- https://iamanc.github.io/post/erpnext-ssti-bug-2
- https://www.notion.so/SSTI-bug-2-239e6086eadc80878e8fcc7b6c26a584?source=copy_link
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66435.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66435
