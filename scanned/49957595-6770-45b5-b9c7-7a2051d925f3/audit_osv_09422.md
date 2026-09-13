# [M] CVE-2016-9828

## Summary
Severity: Medium
Advisory: CVE-2016-9828
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-9828
Type: osv

## Details
The dumpBuffer function in read.c in the listswf tool in libming 0.4.7 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted SWF file.

## References
- http://www.securityfocus.com/bid/94627
- http://www.openwall.com/lists/oss-security/2016/12/05/3
- http://www.openwall.com/lists/oss-security/2016/12/01/8
- https://blogs.gentoo.org/ago/2016/12/01/libming-listswf-null-pointer-dereference-in-dumpbuffer-read-c/
