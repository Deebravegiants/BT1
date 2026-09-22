# [H] CVE-2019-5018

## Summary
Severity: High
Advisory: CVE-2019-5018
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-10
Source: https://osv.dev/vulnerability/CVE-2019-5018
Type: osv

## Details
An exploitable use after free vulnerability exists in the window function functionality of Sqlite3 3.26.0. A specially crafted SQL command can cause a use after free vulnerability, potentially resulting in remote code execution. An attacker can send a malicious SQL command to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/108294
- http://packetstormsecurity.com/files/152809/Sqlite3-Window-Function-Remote-Code-Execution.html
- https://security.gentoo.org/glsa/201908-09
- https://security.netapp.com/advisory/ntap-20190521-0001/
- https://usn.ubuntu.com/4205-1/
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0777
