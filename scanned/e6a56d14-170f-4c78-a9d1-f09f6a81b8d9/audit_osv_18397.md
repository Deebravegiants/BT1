# [H] CVE-2020-27209

## Summary
Severity: High
Advisory: CVE-2020-27209
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2020-27209
Type: osv

## Details
The ECDSA operation of the micro-ecc library 1.0 is vulnerable to simple power analysis attacks which allows an adversary to extract the private ECC key.

## References
- https://eprint.iacr.org/2021/640
- https://github.com/kmackay/micro-ecc/releases
- https://www.aisec.fraunhofer.de/de/das-institut/wissenschaftliche-exzellenz/security-and-trust-in-open-source-security-tokens.html
- https://www.aisec.fraunhofer.de/en/FirmwareProtection.html
- https://github.com/kmackay/micro-ecc/commit/1b5f5cea5145c96dd8791b9b2c41424fc74c2172
