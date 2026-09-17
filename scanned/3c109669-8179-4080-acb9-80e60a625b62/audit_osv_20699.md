# [C] CVE-2021-36219

## Summary
Severity: Critical
Advisory: CVE-2021-36219
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-27
Source: https://osv.dev/vulnerability/CVE-2021-36219
Type: osv

## Details
An issue was discovered in SKALE sgxwallet 1.58.3. The provided input for ECALL 14 triggers a branch in trustedEcdsaSign that frees a non-initialized pointer from the stack. An attacker can chain multiple enclave calls to prepare a stack that contains a valid address. This address is then freed, resulting in compromised integrity of the enclave. This was resolved after v1.58.3 and not reproducible in sgxwallet v1.77.0.

## References
- https://github.com/skalenetwork/sgxwallet/releases
- https://github.com/skalenetwork/sgxwallet/commit/4e9b5b7526db083177e81f8bafeaa4914d276a82
