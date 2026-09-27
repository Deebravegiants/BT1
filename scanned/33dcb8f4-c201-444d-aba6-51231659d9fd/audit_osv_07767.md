# [H] BIT-vault-2020-16251

## Summary
Severity: High
Advisory: BIT-vault-2020-16251
Aliases: CVE-2020-16251, GHSA-4mp7-2m29-gqxf, GO-2024-2488
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2020-16251
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.5.0 <1.5.1

## Details
HashiCorp Vault and Vault Enterprise versions 0.8.3 and newer, when configured with the GCP GCE auth method, may be vulnerable to authentication bypass. Fixed in 1.2.5, 1.3.8, 1.4.4, and 1.5.1.

## References
- http://packetstormsecurity.com/files/159479/Hashicorp-Vault-GCP-IAM-Integration-Authentication-Bypass.html
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#151
- https://www.hashicorp.com/blog/category/vault/
- https://nvd.nist.gov/vuln/detail/CVE-2020-16251
