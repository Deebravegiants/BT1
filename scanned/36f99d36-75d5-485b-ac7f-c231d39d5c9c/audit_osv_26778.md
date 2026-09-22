# [C] phpfm 1.7.9 Authentication Bypass via Type Juggling Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-53894
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2023-53894
Type: osv

## Details
phpfm 1.7.9 contains an authentication bypass vulnerability that allows attackers to log in by exploiting loose type comparison in password hash validation. Attackers can craft specific password hashes beginning with 0e or 00e to bypass authentication and upload malicious PHP files to the server.

## References
- https://www.dulldusk.com/phpfm/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53894.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53894
- https://www.vulncheck.com/advisories/phpfm-authentication-bypass-via-type-juggling-vulnerability
- https://www.exploit-db.com/exploits/51594
