# [H] CVE-2017-1000148

## Summary
Severity: High
Advisory: CVE-2017-1000148
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-03
Source: https://osv.dev/vulnerability/CVE-2017-1000148
Type: osv

## Details
Mahara 15.04 before 15.04.8 and 15.10 before 15.10.4 and 16.04 before 16.04.2 are vulnerable to PHP code execution as Mahara would pass portions of the XML through the PHP "unserialize()" function when importing a skin from an XML file.

## References
- https://bugs.launchpad.net/mahara/+bug/1508684
