# [H] Vault Enterprise vulnerable to cross-namespace entity deletion

## Summary
Severity: High
Advisory: BIT-vault-2026-14886
Aliases: CVE-2026-14886
Ecosystem: Bitnami
Published: 2026-08-24
Source: https://osv.dev/vulnerability/BIT-vault-2026-14886
Type: osv

## Affected
- Bitnami: `vault` — affected >=2.0.0 <2.0.4

## Details
Vault Enterprise's identity entity batch-delete endpoint is vulnerable to a cross-namespace authorization bypass that may allow an authenticated caller in one namespace to permanently delete the storage backing of entities belonging to another namespace. This vulnerability (CVE-2026-14886) is fixed in Vault Enterprise 2.0.4, 1.21.9, 1.20.14 and 1.19.20.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-27-vault-enterprise-vulnerable-to-cross-namespace-entity-deletion/77634
- https://nvd.nist.gov/vuln/detail/CVE-2026-14886
