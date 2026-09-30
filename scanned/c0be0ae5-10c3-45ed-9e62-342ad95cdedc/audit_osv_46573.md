# [M] CVE-2013-7440

## Summary
Severity: Medium
Advisory: CVE-2013-7440
Aliases: PSF-2016-1
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-06-07
Source: https://osv.dev/vulnerability/CVE-2013-7440
Type: osv

## Details
The ssl.match_hostname function in CPython (aka Python) before 2.7.9 and 3.x before 3.3.3 does not properly handle wildcards in hostnames, which might allow man-in-the-middle attackers to spoof servers via a crafted certificate.

## References
- https://access.redhat.com/errata/RHSA-2016:1166
- https://bugzilla.redhat.com/show_bug.cgi?id=1224999
- http://seclists.org/oss-sec/2015/q2/483
- http://seclists.org/oss-sec/2015/q2/523
- http://www.securityfocus.com/bid/74707
- https://bugs.python.org/issue17997
- https://hg.python.org/cpython/rev/10d0edadbcdd
