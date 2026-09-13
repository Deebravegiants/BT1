# [M] CVE-2021-40528

## Summary
Severity: Medium
Advisory: CVE-2021-40528
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-06
Source: https://osv.dev/vulnerability/CVE-2021-40528
Type: osv

## Details
The ElGamal implementation in Libgcrypt before 1.9.4 allows plaintext recovery because, during interaction between two cryptographic libraries, a certain dangerous combination of the prime defined by the receiver's public key, the generator defined by the receiver's public key, and the sender's ephemeral exponents can lead to a cross-configuration attack against OpenPGP.

## References
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=commit%3Bh=3462280f2e23e16adf3ed5176e0f2413d8861320
- https://eprint.iacr.org/2021/923
- https://ibm.github.io/system-security-research-updates/2021/07/20/insecurity-elgamal-pt1
- https://security.gentoo.org/glsa/202210-13
- https://ibm.github.io/system-security-research-updates/2021/09/06/insecurity-elgamal-pt2
