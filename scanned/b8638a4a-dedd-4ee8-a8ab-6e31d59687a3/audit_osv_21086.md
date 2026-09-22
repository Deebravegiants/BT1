# [M] CVE-2021-40530

## Summary
Severity: Medium
Advisory: CVE-2021-40530
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-06
Source: https://osv.dev/vulnerability/CVE-2021-40530
Type: osv

## Details
The ElGamal implementation in Crypto++ through 8.5 allows plaintext recovery because, during interaction between two cryptographic libraries, a certain dangerous combination of the prime defined by the receiver's public key, the generator defined by the receiver's public key, and the sender's ephemeral exponents can lead to a cross-configuration attack against OpenPGP.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/57OJA2K5AHX5HAU2QBDRWLGIIUX7GASC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HGVBZ2TTRKCTYAZTRHTF6OBD4W37F5MT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VJYOZGWI7TD27SEXILSM6VUTPPEICDL7/
- https://eprint.iacr.org/2021/923
- https://ibm.github.io/system-security-research-updates/2021/07/20/insecurity-elgamal-pt1
- https://ibm.github.io/system-security-research-updates/2021/09/06/insecurity-elgamal-pt2
