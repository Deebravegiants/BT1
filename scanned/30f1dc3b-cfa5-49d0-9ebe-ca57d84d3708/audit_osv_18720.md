# [H] CVE-2020-35606

## Summary
Severity: High
Advisory: CVE-2020-35606
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-21
Source: https://osv.dev/vulnerability/CVE-2020-35606
Type: osv

## Details
Arbitrary command execution can occur in Webmin through 1.962. Any user authorized for the Package Updates module can execute arbitrary commands with root privileges via vectors involving %0A and %0C. NOTE: this issue exists because of an incomplete fix for CVE-2019-12840.

## References
- https://www.webmin.com/download.html
- http://packetstormsecurity.com/files/160676/Webmin-1.962-Remote-Command-Execution.html
- https://www.exploit-db.com/exploits/49318
- https://www.pentest.com.tr/exploits/Webmin-1962-PU-Escape-Bypass-Remote-Command-Execution.html
