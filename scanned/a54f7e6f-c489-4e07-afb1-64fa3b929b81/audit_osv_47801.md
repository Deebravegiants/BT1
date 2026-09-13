# [M] CVE-2017-12618

## Summary
Severity: Medium
Advisory: CVE-2017-12618
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-24
Source: https://osv.dev/vulnerability/CVE-2017-12618
Type: osv

## Details
Apache Portable Runtime Utility (APR-util) 1.6.0 and prior fail to validate the integrity of SDBM database files used by apr_sdbm*() functions, resulting in a possible out of bound read access. A local user with write access to the database can make a program or process using these functions crash, and cause a denial of service.

## References
- http://www.securitytracker.com/id/1042004
- https://lists.debian.org/debian-lts-announce/2017/11/msg00006.html
- http://mail-archives.apache.org/mod_mbox/apr-dev/201710.mbox/%3CCACsi252POs4toeJJciwg09_eu2cO3XFg%3DUqsPjXsfjDoeC3-UQ%40mail.gmail.com%3E
- http://www.securityfocus.com/bid/101558
