# [H] GMP has an integer overflow with crafted inputs on 32-bit builds in `int_raw.c`, leading to buffer overflow

## Summary
Severity: High
Advisory: JLSEC-2026-1168
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/JLSEC-2026-1168
Type: osv

## Affected
- Julia: `GCCBootstrap_jll` — affected unspecified
- Julia: `GMP_jll` — affected >=0 <6.3.0+0
- Julia: `LibStdCxx_jll` — affected unspecified

## Details
GNU Multiple Precision Arithmetic Library (GMP) through 6.2.1 has an `mpz/inp_raw.c` integer overflow and resultant buffer overflow via crafted input, leading to a segmentation fault on 32-bit platforms.

## References
- http://seclists.org/fulldisclosure/2022/Oct/8
- http://seclists.org/fulldisclosure/2022/Oct/8
- http://www.openwall.com/lists/oss-security/2022/10/13/3
- http://www.openwall.com/lists/oss-security/2022/10/13/3
- https://bugs.debian.org/994405
- https://bugs.debian.org/994405
- https://gmplib.org/list-archives/gmp-bugs/2021-September/005077.html
- https://gmplib.org/list-archives/gmp-bugs/2021-September/005077.html
- https://gmplib.org/repo/gmp-6.2/rev/561a9c25298e
- https://gmplib.org/repo/gmp-6.2/rev/561a9c25298e
- https://lists.debian.org/debian-lts-announce/2021/12/msg00001.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00001.html
- https://security.gentoo.org/glsa/202309-13
- https://security.gentoo.org/glsa/202309-13
- https://security.netapp.com/advisory/ntap-20221111-0001/
- https://security.netapp.com/advisory/ntap-20221111-0001/
