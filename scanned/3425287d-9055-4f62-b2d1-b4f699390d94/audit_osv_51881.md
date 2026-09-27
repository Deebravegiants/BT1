# [H] CVE-2021-43618

## Summary
Severity: High
Advisory: CVE-2021-43618
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/CVE-2021-43618
Type: osv

## Details
GNU Multiple Precision Arithmetic Library (GMP) through 6.2.1 has an mpz/inp_raw.c integer overflow and resultant buffer overflow via crafted input, leading to a segmentation fault on 32-bit platforms.

## References
- http://www.openwall.com/lists/oss-security/2022/10/13/3
- https://bugs.debian.org/994405
- https://lists.debian.org/debian-lts-announce/2021/12/msg00001.html
- https://security.gentoo.org/glsa/202309-13
- https://security.netapp.com/advisory/ntap-20221111-0001/
- http://seclists.org/fulldisclosure/2022/Oct/8
- https://gmplib.org/repo/gmp-6.2/rev/561a9c25298e
- https://gmplib.org/list-archives/gmp-bugs/2021-September/005077.html
