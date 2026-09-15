# [H] CVE-2018-11237

## Summary
Severity: High
Advisory: CVE-2018-11237
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2018-11237
Type: osv

## Details
An AVX-512-optimized implementation of the mempcpy function in the GNU C Library (aka glibc or libc6) 2.27 and earlier may write data beyond the target buffer, leading to a buffer overflow in __mempcpy_avx512_no_vzeroupper.

## References
- http://www.securityfocus.com/bid/104256
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3092
- https://security.netapp.com/advisory/ntap-20190329-0001/
- https://security.netapp.com/advisory/ntap-20190401-0001/
- https://usn.ubuntu.com/4416-1/
- https://www.exploit-db.com/exploits/44750/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23196
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
