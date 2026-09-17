# [C] BIT-phplist-2020-23361

## Summary
Severity: Critical
Advisory: BIT-phplist-2020-23361
Aliases: CVE-2020-23361
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-phplist-2020-23361
Type: osv

## Affected
- Bitnami: `phplist` — affected >=3.5.3

## Details
phpList 3.5.3 allows type juggling for login bypass because == is used instead of === for password hashes, which mishandles hashes that begin with 0e followed by exclusively numerical characters.

## References
- https://github.com/phpList/phplist3/issues/668
