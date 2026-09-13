# [H] CVE-2015-5343

## Summary
Severity: High
Advisory: CVE-2015-5343
CVSS: 7.6 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2016-04-14
Source: https://osv.dev/vulnerability/CVE-2015-5343
Type: osv

## Details
Integer overflow in util.c in mod_dav_svn in Apache Subversion 1.7.x, 1.8.x before 1.8.15, and 1.9.x before 1.9.3 allows remote authenticated users to cause a denial of service (subversion server crash or memory consumption) and possibly execute arbitrary code via a skel-encoded request body, which triggers an out-of-bounds read and heap-based buffer overflow.

## References
- http://subversion.apache.org/security/CVE-2015-5343-advisory.txt
- http://www.debian.org/security/2015/dsa-3424
- http://www.securitytracker.com/id/1034470
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.405261
