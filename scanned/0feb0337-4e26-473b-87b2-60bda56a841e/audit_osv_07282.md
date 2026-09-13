# [C] BIT-phplist-2020-8547

## Summary
Severity: Critical
Advisory: BIT-phplist-2020-8547
Aliases: CVE-2020-8547
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-phplist-2020-8547
Type: osv

## Affected
- Bitnami: `phplist` — affected >=3.5.0

## Details
phpList 3.5.0 allows type juggling for admin login bypass because == is used instead of === for password hashes, which mishandles hashes that begin with 0e followed by exclusively numerical characters.

## References
- https://www.exploit-db.com/exploits/47989
