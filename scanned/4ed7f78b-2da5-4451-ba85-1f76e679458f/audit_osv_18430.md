# [M] CVE-2020-27618

## Summary
Severity: Medium
Advisory: CVE-2020-27618
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2020-27618
Type: osv

## Details
The iconv function in the GNU C Library (aka glibc or libc6) 2.32 and earlier, when processing invalid multi-byte input sequences in IBM1364, IBM1371, IBM1388, IBM1390, and IBM1399 encodings, fails to advance the input state, which could lead to an infinite loop in applications, resulting in a denial of service, a different vulnerability from CVE-2016-10228.

## References
- https://lists.debian.org/debian-lts-announce/2022/10/msg00021.html
- https://security.gentoo.org/glsa/202107-07
- https://security.netapp.com/advisory/ntap-20210401-0006/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://sourceware.org/bugzilla/show_bug.cgi?id=26224
- https://sourceware.org/bugzilla/show_bug.cgi?id=19519#c21
- https://www.oracle.com/security-alerts/cpujan2022.html
