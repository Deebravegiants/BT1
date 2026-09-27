# [M] BIT-vault-2021-3024

## Summary
Severity: Medium
Advisory: BIT-vault-2021-3024
Aliases: CVE-2021-3024
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2021-3024
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.6.0 <1.6.2

## Details
HashiCorp Vault and Vault Enterprise disclosed the internal IP address of the Vault node when responding to some invalid, unauthenticated HTTP requests. Fixed in 1.6.2 & 1.5.7.

## References
- https://discuss.hashicorp.com/t/hcsec-2021-02-vault-api-endpoint-exposed-internal-ip-address-without-authentication/20334
- https://security.gentoo.org/glsa/202207-01
- https://nvd.nist.gov/vuln/detail/CVE-2021-3024
