# [H] CVE-2021-3326

## Summary
Severity: High
Advisory: CVE-2021-3326
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-27
Source: https://osv.dev/vulnerability/CVE-2021-3326
Type: osv

## Details
The iconv function in the GNU C Library (aka glibc or libc6) 2.32 and earlier, when processing invalid input sequences in the ISO-2022-JP-3 encoding, fails an assertion in the code path and aborts the program, potentially resulting in a denial of service.

## References
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://sourceware.org/git/?p=glibc.git%3Ba=commit%3Bh=7d88c6142c6efc160c0ee5e4f85cde382c072888
- http://www.openwall.com/lists/oss-security/2021/01/28/2
- https://lists.debian.org/debian-lts-announce/2022/10/msg00021.html
- https://security.gentoo.org/glsa/202107-07
- https://security.netapp.com/advisory/ntap-20210304-0007/
- https://sourceware.org/bugzilla/show_bug.cgi?id=27256
- https://www.oracle.com/security-alerts/cpujan2022.html
