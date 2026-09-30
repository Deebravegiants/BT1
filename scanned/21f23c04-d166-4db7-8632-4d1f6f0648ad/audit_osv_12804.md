# [H] CVE-2018-15139

## Summary
Severity: High
Advisory: CVE-2018-15139
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-13
Source: https://osv.dev/vulnerability/CVE-2018-15139
Type: osv

## Details
Unrestricted file upload in interface/super/manage_site_files.php in versions of OpenEMR before 5.0.1.4 allows a remote authenticated attacker to execute arbitrary PHP code by uploading a file with a PHP extension via the images upload form and accessing it in the images directory.

## References
- https://github.com/openemr/openemr/pull/1757/commits/c2808a0493243f618bbbb3459af23c7da3dc5485
- http://packetstormsecurity.com/files/163110/OpenEMR-5.0.1.3-Shell-Upload.html
- http://packetstormsecurity.com/files/163482/OpenEMR-5.0.1.3-Shell-Upload.html
- https://github.com/Hacker5preme/Exploits/tree/main/CVE-2018-15139-Exploit
- https://www.databreaches.net/openemr-patches-serious-vulnerabilities-uncovered-by-project-insecurity/
