# [H] CVE-2020-15176

## Summary
Severity: High
Advisory: CVE-2020-15176
Aliases: GHSA-x93w-64x9-58qw
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2020-10-07
Source: https://osv.dev/vulnerability/CVE-2020-15176
Type: osv

## Details
In GLPI before version 9.5.2, when supplying a back tick in input that gets put into a SQL query,the application does not escape or sanitize allowing for SQL Injection to occur. Leveraging this vulnerability an attacker is able to exfiltrate sensitive information like passwords, reset tokens, personal details, and more. The issue is patched in version 9.5.2

## References
- https://github.com/glpi-project/glpi/security/advisories/GHSA-x93w-64x9-58qw
- https://github.com/glpi-project/glpi/commit/f021f1f365b4acea5066d3e57c6d22658cf32575
