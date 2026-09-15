# [M] CVE-2018-0495

## Summary
Severity: Medium
Advisory: CVE-2018-0495
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-0495
Type: osv

## Details
Libgcrypt before 1.7.10 and 1.8.x before 1.8.3 allows a memory-cache side-channel attack on ECDSA signatures that can be mitigated through the use of blinding during the signing process in the _gcry_ecc_ecdsa_sign function in cipher/ecc-ecdsa.c, aka the Return Of the Hidden Number Problem or ROHNP. To discover an ECDSA key, the attacker needs access to either the local machine or a different virtual machine on the same physical host.

## References
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=commit%3Bh=9010d1576e278a4274ad3f4aa15776c28f6ba965
- http://www.securitytracker.com/id/1041144
- http://www.securitytracker.com/id/1041147
- https://access.redhat.com/errata/RHSA-2018:3221
- https://access.redhat.com/errata/RHSA-2018:3505
- https://access.redhat.com/errata/RHSA-2019:1296
- https://access.redhat.com/errata/RHSA-2019:1297
- https://access.redhat.com/errata/RHSA-2019:1543
- https://access.redhat.com/errata/RHSA-2019:2237
- https://lists.debian.org/debian-lts-announce/2018/06/msg00013.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2018q2/000426.html
- https://usn.ubuntu.com/3689-1/
- https://usn.ubuntu.com/3689-2/
- https://usn.ubuntu.com/3692-1/
- https://usn.ubuntu.com/3692-2/
- https://usn.ubuntu.com/3850-1/
- https://usn.ubuntu.com/3850-2/
- https://www.debian.org/security/2018/dsa-4231
- https://dev.gnupg.org/T4011
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
