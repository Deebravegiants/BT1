# [H] CVE-2018-19908

## Summary
Severity: High
Advisory: CVE-2018-19908
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-19908
Type: osv

## Details
An issue was discovered in MISP 2.4.9x before 2.4.99. In app/Model/Event.php (the STIX 1 import code), an unescaped filename string is used to construct a shell command. This vulnerability can be abused by a malicious authenticated user to execute arbitrary commands by tweaking the original filename of the STIX import.

## References
- https://github.com/MISP/MISP/releases/tag/v2.4.99
- https://github.com/MISP/MISP/commit/211ac0737281b65e7da160f0aac52f401a94e1a3
- https://www.exploit-db.com/exploits/46401/
