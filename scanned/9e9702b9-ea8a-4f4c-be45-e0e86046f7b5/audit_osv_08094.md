# [M] CVE-2016-10228

## Summary
Severity: Medium
Advisory: CVE-2016-10228
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2016-10228
Type: osv

## Details
The iconv program in the GNU C Library (aka glibc or libc6) 2.31 and earlier, when invoked with multiple suffixes in the destination encoding (TRANSLATE or IGNORE) along with the -c option, enters an infinite loop when processing invalid multi-byte input sequences, leading to a denial of service.

## References
- http://www.securityfocus.com/bid/96525
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2022/10/msg00021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- http://openwall.com/lists/oss-security/2017/03/01/10
- https://security.gentoo.org/glsa/202101-20
- https://sourceware.org/bugzilla/show_bug.cgi?id=19519
- https://sourceware.org/bugzilla/show_bug.cgi?id=19519#c21
- https://sourceware.org/bugzilla/show_bug.cgi?id=26224
