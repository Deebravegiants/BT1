# [H] CVE-2018-6829

## Summary
Severity: High
Advisory: CVE-2018-6829
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-07
Source: https://osv.dev/vulnerability/CVE-2018-6829
Type: osv

## Details
cipher/elgamal.c in Libgcrypt through 1.8.2, when used to encrypt messages directly, improperly encodes plaintexts, which allows attackers to obtain sensitive information by reading ciphertext data (i.e., it does not have semantic security in face of a ciphertext-only attack). The Decisional Diffie-Hellman (DDH) assumption does not hold for Libgcrypt's ElGamal implementation.

## References
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://github.com/weikengchen/attack-on-libgcrypt-elgamal
- https://lists.gnupg.org/pipermail/gcrypt-devel/2018-February/004394.html
- https://github.com/weikengchen/attack-on-libgcrypt-elgamal/wiki
