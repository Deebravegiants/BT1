# [C] eXtplorer<= 2.1.14 - Authentication Bypass & Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2023-54335
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2023-54335
Type: osv

## Details
eXtplorer 2.1.14 contains an authentication bypass vulnerability that allows attackers to login without a password by manipulating the login request. Attackers can exploit this flaw to upload malicious PHP files and execute remote commands on the vulnerable file management system.

## References
- https://extplorer.net/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54335.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54335
- https://www.vulncheck.com/advisories/extplorer-authentication-bypass-remote-code-execution-rce
- https://www.exploit-db.com/exploits/51067
