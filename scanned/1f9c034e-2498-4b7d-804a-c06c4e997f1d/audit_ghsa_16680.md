# [H] doctrine/orm Regression in Query Parenthesis can have Security Implications

## Summary
Severity: High
Advisory: GHSA-vjrg-wpm8-rhrw
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-vjrg-wpm8-rhrw
Type: github-advisory

## Affected
- Packagist: `doctrine/orm` — affected >=2.8.3 <2.8.4

## Details
An issue identified in doctrine/orm project related to statement in Where-Clause were not wrapped in brackets due to improper hadandling of case insensitive check.

## References
- https://github.com/doctrine/orm/pull/8591
- https://github.com/FriendsOfPHP/security-advisories/blob/master/doctrine/orm/2021-04-06.yaml
- https://github.com/doctrine/orm
