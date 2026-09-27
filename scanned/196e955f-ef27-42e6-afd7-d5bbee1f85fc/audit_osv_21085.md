# [M] CVE-2021-40529

## Summary
Severity: Medium
Advisory: CVE-2021-40529
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-06
Source: https://osv.dev/vulnerability/CVE-2021-40529
Type: osv

## Details
The ElGamal implementation in Botan through 2.18.1, as used in Thunderbird and other products, allows plaintext recovery because, during interaction between two cryptographic libraries, a certain dangerous combination of the prime defined by the receiver's public key, the generator defined by the receiver's public key, and the sender's ephemeral exponents can lead to a cross-configuration attack against OpenPGP.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/72NB4OLD3VHJC3YF3PEP2HKF6BYURPAO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UPHGYWNJQKWLTUWBNSFB4F66MQDIL3IB/
- https://eprint.iacr.org/2021/923
- https://ibm.github.io/system-security-research-updates/2021/07/20/insecurity-elgamal-pt1
- https://security.gentoo.org/glsa/202208-14
- https://github.com/randombit/botan/pull/2790
- https://ibm.github.io/system-security-research-updates/2021/09/06/insecurity-elgamal-pt2
