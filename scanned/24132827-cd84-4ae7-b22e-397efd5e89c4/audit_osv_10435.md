# [C] CVE-2017-15580

## Summary
Severity: Critical
Advisory: CVE-2017-15580
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-23
Source: https://osv.dev/vulnerability/CVE-2017-15580
Type: osv

## Details
osTicket 1.10.1 provides a functionality to upload 'html' files with associated formats. However, it does not properly validate the uploaded file's contents and thus accepts any type of file, such as with a tickets.php request that is modified with a .html extension changed to a .exe extension. An attacker can leverage this vulnerability to upload arbitrary files on the web application having malicious content.

## References
- http://0day.today/exploits/28864
- http://nakedsecurity.com/cve/CVE-2017-15580/
- https://www.cyber-security.ro/blog/2017/10/25/osticket-1-10-1-shell-upload/
- https://becomepentester.blogspot.com/2017/10/osTicket-File-Upload-Restrictions-Bypassed-CVE-2017-15580.html
- https://cxsecurity.com/issue/WLB-2017100187
- https://packetstormsecurity.com/files/144747/osticket1101-shell.txt
- https://www.exploit-db.com/exploits/45169/
