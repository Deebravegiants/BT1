# [H] CVE-2021-40309

## Summary
Severity: High
Advisory: CVE-2021-40309
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-24
Source: https://osv.dev/vulnerability/CVE-2021-40309
Type: osv

## Details
A SQL injection vulnerability exists in the Take Attendance functionality of OS4Ed's OpenSIS 8.0. allows an attacker to inject their own SQL query. The cp_id_miss_attn parameter from TakeAttendance.php is vulnerable to SQL injection. An attacker can make an authenticated HTTP request as a user with access to "Take Attendance" functionality to trigger this vulnerability.

## References
- https://github.com/OS4ED/openSIS-Classic
- https://github.com/MiSERYYYYY/Vulnerability-Reports-and-Disclosures/blob/main/OpenSIS-Community-8.0.md
- https://www.exploit-db.com/exploits/50249
