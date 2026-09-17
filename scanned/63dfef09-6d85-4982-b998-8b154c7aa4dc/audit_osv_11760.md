# [M] CVE-2017-9526

## Summary
Severity: Medium
Advisory: CVE-2017-9526
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-11
Source: https://osv.dev/vulnerability/CVE-2017-9526
Type: osv

## Details
In Libgcrypt before 1.7.7, an attacker who learns the EdDSA session key (from side-channel observation during the signing process) can easily recover the long-term secret key. 1.7.7 makes a cipher/ecc-eddsa.c change to store this session key in secure memory, to ensure that constant-time point operations are used in the MPI library.

## References
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=commit%3Bh=5a22de904a0a366ae79f03ff1e13a1232a89e26b
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=commit%3Bh=f9494b3f258e01b6af8bd3941ce436bcc00afc56
- http://www.debian.org/security/2017/dsa-3880
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.securityfocus.com/bid/99046
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://bugzilla.suse.com/show_bug.cgi?id=1042326
