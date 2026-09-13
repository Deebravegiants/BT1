# [M] BIT-redash-2020-36144

## Summary
Severity: Medium
Advisory: BIT-redash-2020-36144
Aliases: CVE-2020-36144
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redash-2020-36144
Type: osv

## Affected
- Bitnami: `redash` — affected >=8.0.0

## Details
Redash 8.0.0 is affected by LDAP Injection. There is an information leak through the crafting of special queries, escaping the provided template since the username included in the search filter lacks sanitization.

## References
- https://github.com/getredash/redash/issues/5426
- https://github.com/getredash/redash/releases
