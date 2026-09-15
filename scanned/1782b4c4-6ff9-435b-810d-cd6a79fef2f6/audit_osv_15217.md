# [H] CVE-2019-14530

## Summary
Severity: High
Advisory: CVE-2019-14530
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/CVE-2019-14530
Type: osv

## Details
An issue was discovered in custom/ajax_download.php in OpenEMR before 5.0.2 via the fileName parameter. An attacker can download any file (that is readable by the user www-data) from server storage. If the requested file is writable for the www-data user and the directory /var/www/openemr/sites/default/documents/cqm_qrda/ exists, it will be deleted from server.

## References
- https://github.com/openemr/openemr/pull/2592
- http://packetstormsecurity.com/files/163215/OpenEMR-5.0.1.7-Path-Traversal.html
- http://packetstormsecurity.com/files/163375/OpenEMR-5.0.1.7-Path-Traversal.html
- https://github.com/Hacker5preme/Exploits/tree/main/CVE-2019-14530-Exploit
- https://github.com/Wezery/CVE-2019-14530
