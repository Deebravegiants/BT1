# [M] BIT-espocrm-2024-24818

## Summary
Severity: Medium
Advisory: BIT-espocrm-2024-24818
Aliases: CVE-2024-24818, GHSA-8gv6-8r33-fm7j
Ecosystem: Bitnami
Published: 2024-03-31
Source: https://osv.dev/vulnerability/BIT-espocrm-2024-24818
Type: osv

## Affected
- Bitnami: `espocrm` — affected >=0 <8.1.2

## Details
EspoCRM is an Open Source Customer Relationship Management software. An attacker can inject arbitrary IP or domain in "Password Change" page and redirect victim to malicious page that could lead to  credential stealing or another attack. This vulnerability is fixed in 8.1.2.

## References
- https://github.com/espocrm/espocrm/commit/3babdfa3399e328fb1bd83a1b4ed03d509f4c8e7
- https://github.com/espocrm/espocrm/security/advisories/GHSA-8gv6-8r33-fm7j
