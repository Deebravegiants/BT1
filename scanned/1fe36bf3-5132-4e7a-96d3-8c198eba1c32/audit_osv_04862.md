# [M] BIT-ghost-2022-41697

## Summary
Severity: Medium
Advisory: BIT-ghost-2022-41697
Aliases: CVE-2022-41697
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ghost-2022-41697
Type: osv

## Affected
- Bitnami: `ghost` — affected >=5.9.4 <5.9.5

## Details
A user enumeration vulnerability exists in the login functionality of Ghost Foundation Ghost 5.9.4. A specially-crafted HTTP request can lead to a disclosure of sensitive information. An attacker can send a series of HTTP requests to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1625
- https://nvd.nist.gov/vuln/detail/CVE-2022-41697
