# [M] Vault's Transit Secrets Engine Allowed Nonce Specified without Convergent Encryption

## Summary
Severity: Medium
Advisory: BIT-vault-2023-4680
Aliases: CVE-2023-4680, GHSA-v84f-6r39-cpfc, GO-2023-2063
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2023-4680
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.14.0 <1.14.3

## Details
HashiCorp Vault and Vault Enterprise transit secrets engine allowed authorized users to specify arbitrary nonces, even with convergent encryption disabled. The encrypt endpoint, in combination with an offline attack, could be used to decrypt arbitrary ciphertext and potentially derive the authentication subkey when using transit secrets engine without convergent encryption. Introduced in 1.6.0 and fixed in 1.14.3, 1.13.7, and 1.12.11.

## References
- https://discuss.hashicorp.com/t/hcsec-2023-28-vault-s-transit-secrets-engine-allowed-nonce-specified-without-convergent-encryption/58249
- https://nvd.nist.gov/vuln/detail/CVE-2023-4680
