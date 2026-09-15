# [H] CVE-2017-5331

## Summary
Severity: High
Advisory: CVE-2017-5331
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-04
Source: https://osv.dev/vulnerability/CVE-2017-5331
Type: osv

## Details
Integer overflow in the check_offset function in b/wrestool/fileread.c in icoutils before 0.31.1 allows local users to cause a denial of service (process crash) and execute arbitrary code via a crafted executable.

## References
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00026.html
- http://www.debian.org/security/2017/dsa-3765
- http://www.securityfocus.com/bid/95378
- http://www.ubuntu.com/usn/USN-3178-1
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00025.html
- http://www.openwall.com/lists/oss-security/2017/01/11/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1412248
