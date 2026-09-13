# [C] Frappe Framework ERPNext 13.4.0 Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2023-54345
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2023-54345
Type: osv

## Details
Frappe Framework ERPNext 13.4.0 contains a sandbox escape vulnerability in RestrictedPython that allows authenticated users with System Manager role to execute arbitrary code by exploiting frame introspection. Attackers can create a server script via the /app/server-script endpoint and access the gi_frame attribute to traverse the call stack and invoke os.popen to execute system commands.

## References
- http://erpnext.org
- https://gist.github.com/lebr0nli/c2fc617390451f0e5a4c31c87d8720b6
- https://github.com/frappe/frappe/
- https://github.com/frappe/frappe/blob/v13.4.0/frappe/utils/safe_exec.py#L42
- https://frappeframework.com/docs/v13/user/en/desk/scripting/server-script
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54345.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54345
- https://ur4ndom.dev/posts/2023-07-02-uiuctf-rattler-read/
- https://www.vulncheck.com/advisories/frappe-framework-erpnext-remote-code-execution
- https://www.exploit-db.com/exploits/51580
