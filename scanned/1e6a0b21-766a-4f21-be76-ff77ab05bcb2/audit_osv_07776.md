# [M] BIT-vault-2021-41802

## Summary
Severity: Medium
Advisory: BIT-vault-2021-41802
Aliases: CVE-2021-41802, GHSA-qv95-g3gm-x542, GO-2022-0618
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2021-41802
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.8.0 <1.8.4

## Details
HashiCorp Vault and Vault Enterprise through 1.7.4 and 1.8.3 allowed a user with write permission to an entity alias ID sharing a mount accessor with another user to acquire this other user’s policies by merging their identities. Fixed in Vault and Vault Enterprise 1.7.5 and 1.8.4.

## References
- https://discuss.hashicorp.com/t/hcsec-2021-27-vault-merging-multiple-entity-aliases-for-the-same-mount-may-allow-privilege-escalation/
- https://security.gentoo.org/glsa/202207-01
- https://nvd.nist.gov/vuln/detail/CVE-2021-41802
