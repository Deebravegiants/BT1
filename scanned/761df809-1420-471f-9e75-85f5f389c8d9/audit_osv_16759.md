# [H] CVE-2019-9624

## Summary
Severity: High
Advisory: CVE-2019-9624
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-07
Source: https://osv.dev/vulnerability/CVE-2019-9624
Type: osv

## Details
Webmin 1.900 allows remote attackers to execute arbitrary code by leveraging the "Java file manager" and "Upload and Download" privileges to upload a crafted .cgi file via the /updown/upload.cgi URI.

## References
- http://www.rapid7.com/db/modules/exploit/unix/webapp/webmin_upload_exec
- https://pentest.com.tr/exploits/Webmin-1900-Remote-Command-Execution.html
- https://www.exploit-db.com/exploits/46201
