# [H] phpPgAdmin contains a remote command execution vulnerability

## Summary
Severity: High
Advisory: GHSA-86gh-c8r8-xwhq
CVE: CVE-2021-47853
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-86gh-c8r8-xwhq
Type: github-advisory

## Affected
- Packagist: `phppgadmin/phppgadmin` — affected >=0

## Details
phpPgAdmin 7.13.0 contains a remote command execution vulnerability that allows authenticated attackers to execute arbitrary system commands through SQL query manipulation. Attackers can create a custom table, upload a malicious .txt file, and use the COPY FROM PROGRAM command to execute operating system commands with the application's privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-47853
- https://github.com/phppgadmin/phppgadmin
- https://github.com/phppgadmin/phppgadmin/releases
- https://www.exploit-db.com/exploits/49736
- https://www.vulncheck.com/advisories/phppgadmin-copy-from-program-command-execution
