# [H] CVE-2018-14857

## Summary
Severity: High
Advisory: CVE-2018-14857
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-06
Source: https://osv.dev/vulnerability/CVE-2018-14857
Type: osv

## Details
Unrestricted file upload (with remote code execution) in require/mail/NotificationMail.php in Webconsole in OCS Inventory NG OCS Inventory Server through 2.5 allows a privileged user to gain access to the server via a template file containing PHP code, because file extensions other than .html are permitted.

## References
- http://seclists.org/fulldisclosure/2018/Aug/6
- http://www.securitytracker.com/id/1041418
- https://github.com/OCSInventory-NG/OCSInventory-ocsreports/commit/cc572819e373f7ff81dec61591b6f465b43c5515
