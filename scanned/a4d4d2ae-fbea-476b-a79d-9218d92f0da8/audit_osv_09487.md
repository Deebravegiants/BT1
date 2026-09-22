# [H] CVE-2017-0379

## Summary
Severity: High
Advisory: CVE-2017-0379
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-0379
Type: osv

## Details
Libgcrypt before 1.8.1 does not properly consider Curve25519 side-channel attacks, which makes it easier for attackers to discover a secret key, related to cipher/ecc.c and mpi/ec.c.

## References
- http://www.securitytracker.com/id/1041294
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=commit%3Bh=da780c8183cccc8f533c8ace8211ac2cb2bdee7b
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.securityfocus.com/bid/100503
- https://eprint.iacr.org/2017/806
- https://security.netapp.com/advisory/ntap-20180726-0002/
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://bugs.debian.org/873383
- https://lists.debian.org/debian-security-announce/2017/msg00221.html
- https://security-tracker.debian.org/tracker/CVE-2017-0379
- https://www.debian.org/security/2017/dsa-3959
