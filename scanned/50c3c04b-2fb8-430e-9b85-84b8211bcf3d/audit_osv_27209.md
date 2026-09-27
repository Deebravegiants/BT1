# [C] Webmin CGI Command Injection Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-12828
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-12-30
Source: https://osv.dev/vulnerability/CVE-2024-12828
Type: osv

## Details
Webmin CGI Command Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Webmin. Authentication is required to exploit this vulnerability. 

The specific flaw exists within the handling of CGI requests. The issue results from the lack of proper validation of a user-supplied string before using it to execute a system call. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-22346.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12828.json
- https://github.com/webmin/authentic-theme/commit/61e5b10227b50407e3c6ac494ffbd4385d1b59df
- https://nvd.nist.gov/vuln/detail/CVE-2024-12828
- https://www.zerodayinitiative.com/advisories/ZDI-24-1725/
