# [H] CVE-2025-66437

## Summary
Severity: High
Advisory: CVE-2025-66437
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-66437
Type: osv

## Details
An SSTI (Server-Side Template Injection) vulnerability exists in the get_address_display method of Frappe ERPNext through 15.89.0. This function renders address templates using frappe.render_template() with a context derived from the address_dict parameter, which can be either a dictionary or a string referencing an Address document. Although ERPNext uses a custom Jinja2 SandboxedEnvironment, dangerous functions like frappe.db.sql remain accessible via get_safe_globals(). An authenticated attacker with permission to create or modify an Address Template can inject arbitrary Jinja expressions into the template field. By creating an Address document with a matching country, and then calling the get_address_display API with address_dict="address_name", the system will render the malicious template using attacker-controlled data. This leads to server-side code execution or database information disclosure.

## References
- https://iamanc.github.io/post/erpnext-ssti-bug-4
- https://www.notion.so/SSTI-bug-4-239e6086eadc80aa9331fba874c674a5?source=copy_link
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66437.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66437
