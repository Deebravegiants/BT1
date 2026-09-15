# [H] CVE-2020-28021

## Summary
Severity: High
Advisory: CVE-2020-28021
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28021
Type: osv

## Details
Exim 4 before 4.94.2 has Improper Neutralization of Line Delimiters. An authenticated remote SMTP client can insert newline characters into a spool file (which indirectly leads to remote code execution as root) via AUTH= in a MAIL FROM command.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28021-MAUTH.txt
