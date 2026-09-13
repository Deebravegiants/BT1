# [H] CVE-2016-1499

## Summary
Severity: High
Advisory: CVE-2016-1499
CVSS: 8.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:H)
Published: 2016-01-08
Source: https://osv.dev/vulnerability/CVE-2016-1499
Type: osv

## Details
ownCloud Server before 8.0.10, 8.1.x before 8.1.5, and 8.2.x before 8.2.2 allow remote authenticated users to obtain sensitive information from a directory listing and possibly cause a denial of service (CPU consumption) via the force parameter to index.php/apps/files/ajax/scan.php.

## References
- http://packetstormsecurity.com/files/135158/ownCloud-8.2.1-8.1.4-8.0.9-Information-Exposure.html
- http://www.securityfocus.com/archive/1/537244/100/0/threaded
- http://www.securityfocus.com/archive/1/537556/100/0/threaded
- https://owncloud.org/security/advisory/?id=oc-sa-2016-002
- https://www.syss.de/fileadmin/dokumente/Publikationen/Advisories/SYSS-2015-062.txt
