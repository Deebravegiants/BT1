# [M] BIT-vault-2021-27668

## Summary
Severity: Medium
Advisory: BIT-vault-2021-27668
Aliases: CVE-2021-27668
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2021-27668
Type: osv

## Affected
- Bitnami: `vault` — affected >=0.9.2 <1.6.3

## Details
HashiCorp Vault Enterprise 0.9.2 through 1.6.2 allowed the read of license metadata from DR secondaries without authentication. Fixed in 1.6.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2021-05-vault-enterprise-s-dr-secondaries-exposed-license-metadata-without-authentication/21427
- https://security.gentoo.org/glsa/202207-01
- https://nvd.nist.gov/vuln/detail/CVE-2021-27668
