# [M] CVE-2017-12586

## Summary
Severity: Medium
Advisory: CVE-2017-12586
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-06
Source: https://osv.dev/vulnerability/CVE-2017-12586
Type: osv

## Details
SLiMS 8 Akasia through 8.3.1 has an arbitrary file reading issue because of directory traversal in the url parameter to admin/help.php. It can be exploited by remote authenticated librarian users.

## References
- https://github.com/slims/slims8_akasia/issues/48
