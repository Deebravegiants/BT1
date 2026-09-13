# [H] Open WebUI load_tool_module_by_id Command Injection Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-0766
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-0766
Type: osv

## Details
Open WebUI load_tool_module_by_id Command Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Open WebUI. Authentication is required to exploit this vulnerability.

The specific flaw exists within the load_tool_module_by_id function. The issue results from the lack of proper validation of a user-supplied string before using it to execute Python code. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-28257.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0766.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0766
- https://www.zerodayinitiative.com/advisories/ZDI-26-032/
