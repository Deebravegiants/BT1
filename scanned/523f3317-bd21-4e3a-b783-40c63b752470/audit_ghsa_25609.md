# [H] SQL injection in ImpressCMS

## Summary
Severity: High
Advisory: GHSA-f99r-jjgr-f373
CVE: CVE-2022-26986
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-f99r-jjgr-f373
Type: github-advisory

## Affected
- Packagist: `impresscms/impresscms` — affected >=0

## Details
SQL Injection in ImpressCMS 1.4.3 and earlier allows remote attackers to inject into the code in unintended way, this allows an attacker to read and modify the sensitive information from the database used by the application. If misconfigured, an attacker can even upload a malicious web shell to compromise the entire system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26986
- https://github.com/ImpressCMS/impresscms
- https://github.com/sartlabs/0days/blob/main/ImpressCMS1.4.3/Exploit.txt
- http://packetstormsecurity.com/files/171485/ImpressCMS-1.4.3-SQL-Injection.html
