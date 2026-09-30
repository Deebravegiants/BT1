# [M] CVE-2014-3591

## Summary
Severity: Medium
Advisory: CVE-2014-3591
CVSS: 4.2 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2014-3591
Type: osv

## Details
Libgcrypt before 1.6.3 and GnuPG before 1.4.19 does not implement ciphertext blinding for Elgamal decryption, which allows physically proximate attackers to obtain the server's private key by determining factors using crafted ciphertext and the fluctuations in the electromagnetic field during multiplication.

## References
- http://www.cs.tau.ac.il/~tromer/radioexp/
- http://www.debian.org/security/2015/dsa-3184
- http://www.debian.org/security/2015/dsa-3185
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000363.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000364.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000363.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000364.html
