# [M] CVE-2020-10029

## Summary
Severity: Medium
Advisory: CVE-2020-10029
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-04
Source: https://osv.dev/vulnerability/CVE-2020-10029
Type: osv

## Details
The GNU C Library (aka glibc or libc6) before 2.32 could overflow an on-stack buffer during range reduction if an input to an 80-bit long double function contains a non-canonical bit pattern, a seen when passing a 0x5d414141414141410000 value to sinl on x86 targets. This is related to sysdeps/ieee754/ldbl-96/e_rem_pio2l.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/23N76M3EDP2GIW4GOIQRYTKRE7PPBRB2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JZTFUD5VH2GU3YOXA2KBQSBIDZRDWNZ3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VU5JJGENOK7K4X5RYAA5PL647C6HD22E/
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Ba=commit%3Bh=9333498794cde1d5cca518badf79533a24114b6f
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00033.html
- https://lists.debian.org/debian-lts-announce/2022/10/msg00021.html
- https://security.gentoo.org/glsa/202006-04
- https://security.netapp.com/advisory/ntap-20200327-0003/
- https://usn.ubuntu.com/4416-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25487
