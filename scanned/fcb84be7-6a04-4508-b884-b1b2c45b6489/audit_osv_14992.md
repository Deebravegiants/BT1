# [H] CVE-2019-12840

## Summary
Severity: High
Advisory: CVE-2019-12840
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-15
Source: https://osv.dev/vulnerability/CVE-2019-12840
Type: osv

## Details
In Webmin through 1.910, any user authorized to the "Package Updates" module can execute arbitrary commands with root privileges via the data parameter to update.cgi.

## References
- http://packetstormsecurity.com/files/153372/Webmin-1.910-Remote-Command-Execution.html
- http://www.securityfocus.com/bid/108790
- https://pentest.com.tr/exploits/Webmin-1910-Package-Updates-Remote-Command-Execution.html
- https://www.exploit-db.com/exploits/46984
