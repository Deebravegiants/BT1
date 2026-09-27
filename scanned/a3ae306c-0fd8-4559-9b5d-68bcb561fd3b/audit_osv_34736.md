# [H] ServiceStack FindType Directory Traversal Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-6445
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-6445
Type: osv

## Details
ServiceStack FindType Directory Traversal Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of ServiceStack. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the implementation of the FindType method. The issue results from the lack of proper validation of a user-supplied path prior to using it in file operations. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-25837.

## References
- https://docs.servicestack.net/releases/v8_06#reported-vulnerabilities
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6445.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6445
- https://www.zerodayinitiative.com/advisories/ZDI-25-416/
