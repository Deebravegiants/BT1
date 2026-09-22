# [H] CVE-2018-19591

## Summary
Severity: High
Advisory: CVE-2018-19591
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/CVE-2018-19591
Type: osv

## Details
In the GNU C Library (aka glibc or libc6) through 2.28, attempting to resolve a crafted hostname via getaddrinfo() leads to the allocation of a socket descriptor that is not closed. This is related to the if_nametoindex() function.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BO7WHN52GFMC5F2I2232GFIPSSXWFV7G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M52KE4YR3GNMHQUOS3DKAGZD5TQ5D5UH/
- https://sourceware.org/git/?p=glibc.git%3Ba=blob_plain%3Bf=NEWS%3Bhb=HEAD
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Ba=commitdiff%3Bh=d527c860f5a3f0ed687bd03f0cb464612dc23408
- https://usn.ubuntu.com/4416-1/
- http://www.securityfocus.com/bid/106037
- http://www.securitytracker.com/id/1042174
- https://security.gentoo.org/glsa/201903-09
- https://security.gentoo.org/glsa/201908-06
- https://security.netapp.com/advisory/ntap-20190321-0003/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23927
