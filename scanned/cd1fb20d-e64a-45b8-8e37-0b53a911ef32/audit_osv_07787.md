# [M] Vault vulnerable to LIST authorization bypass via trailing-slash strip

## Summary
Severity: Medium
Advisory: BIT-vault-2026-12624
Aliases: CVE-2026-12624
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-vault-2026-12624
Type: osv

## Affected
- Bitnami: `vault` — affected >=0 <2.0.3

## Details
Vault’s ACL policy engine did not consistently enforce a wildcard (glob) deny rule against LIST requests made with a trailing slash on the denied path. This may allow a token holding a broader allow rule alongside a narrower wildcard deny rule to enumerate the names of entries beneath a path it was intended to be denied access to. This vulnerability (CVE-2026-12624) is fixed in Vault Community Edition 2.0.3 and Vault Enterprise 2.0.3, 1.21.8, 1.20.13, and 1.19.19.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-26-vault-vulnerable-to-list-authorization-bypass-via-trailing-slash-strip/77632
- https://nvd.nist.gov/vuln/detail/CVE-2026-12624
