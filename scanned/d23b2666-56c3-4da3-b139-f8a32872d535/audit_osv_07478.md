# [M] BIT-seopanel-2024-22647

## Summary
Severity: Medium
Advisory: BIT-seopanel-2024-22647
Aliases: CVE-2024-22647
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-seopanel-2024-22647
Type: osv

## Affected
- Bitnami: `seopanel` — affected >=4.10.0

## Details
An user enumeration vulnerability was found in SEO Panel 4.10.0. This issue occurs during user authentication, where a difference in error messages could allow an attacker to determine if a username is valid or not, enabling a brute-force attack with valid usernames.

## References
- https://github.com/cassis-sec/CVE/tree/main/2024/CVE-2024-22647
