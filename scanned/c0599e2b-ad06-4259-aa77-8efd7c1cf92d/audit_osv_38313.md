# [C] CVE-2026-38431

## Summary
Severity: Critical
Advisory: CVE-2026-38431
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-38431
Type: osv

## Details
ERPNext v15.103.1 and before is vulnerable to Server-Side Template Injection (SSTI). An attacker with permission to create or edit email templates can inject template expressions that are executed on the server when the template is rendered.

## References
- https://c0wking.hashnode.dev/ssti-in-erpnext-frappe-email-template-engine
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38431.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38431
