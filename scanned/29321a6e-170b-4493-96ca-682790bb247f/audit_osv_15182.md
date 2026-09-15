# [M] CVE-2019-14318

## Summary
Severity: Medium
Advisory: CVE-2019-14318
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-14318
Type: osv

## Details
Crypto++ 8.3.0 and earlier contains a timing side channel in ECDSA signature generation. This allows a local or remote attacker, able to measure the duration of hundreds to thousands of signing operations, to compute the private key used. The issue occurs because scalar multiplication in ecp.cpp (prime field curves, small leakage) and algebra.cpp (binary field curves, large leakage) is not constant time and leaks the bit length of the scalar among other information.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00066.html
- http://www.openwall.com/lists/oss-security/2019/10/02/2
- https://minerva.crocs.fi.muni.cz/
- https://tches.iacr.org/index.php/TCHES/article/view/7337
- https://github.com/weidai11/cryptopp/issues/869
- https://eprint.iacr.org/2011/232.pdf
