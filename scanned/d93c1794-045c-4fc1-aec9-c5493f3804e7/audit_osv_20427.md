# [H] CVE-2021-33560

## Summary
Severity: High
Advisory: CVE-2021-33560
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-08
Source: https://osv.dev/vulnerability/CVE-2021-33560
Type: osv

## Details
Libgcrypt before 1.8.8 and 1.9.x before 1.9.3 mishandles ElGamal encryption because it lacks exponent blinding to address a side-channel attack against mpi_powm, and the window size is not chosen appropriately. This, for example, affects use of ElGamal in OpenPGP.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BKKTOIGFW2SGN3DO2UHHVZ7MJSYN4AAB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R7OAPCUGPF3VLA7QAJUQSL255D4ITVTL/
- https://dev.gnupg.org/T5305
- https://dev.gnupg.org/T5328
- https://dev.gnupg.org/T5466
- https://lists.debian.org/debian-lts-announce/2021/06/msg00021.html
- https://security.gentoo.org/glsa/202210-13
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://dev.gnupg.org/rCe8b7f10be275bcedb5fc05ed4837a89bfd605c61
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
