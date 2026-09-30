# [C] win-cli-mcp-server resolveCommandPath Command Injection Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-11202
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-29
Source: https://osv.dev/vulnerability/CVE-2025-11202
Type: osv

## Details
win-cli-mcp-server resolveCommandPath Command Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of win-cli-mcp-server. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the implementation of the resolveCommandPath method. The issue results from the lack of proper validation of a user-supplied string before using it to execute a system call. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-27787.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11202.json
- https://github.com/simon-ami/win-cli-mcp-server/commit/521b4a34190d03bde7d433d213c36357181a6d09
- https://nvd.nist.gov/vuln/detail/CVE-2025-11202
- https://www.zerodayinitiative.com/advisories/ZDI-25-930/
