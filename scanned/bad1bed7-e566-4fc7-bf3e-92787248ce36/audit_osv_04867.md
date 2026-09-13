# [M] BIT-ghost-2023-26510

## Summary
Severity: Medium
Advisory: BIT-ghost-2023-26510
Aliases: CVE-2023-26510
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ghost-2023-26510
Type: osv

## Affected
- Bitnami: `ghost` — affected >=5.35.0 <5.35.1

## Details
Ghost 5.35.0 allows authorization bypass: contributors can view draft posts of other users, which is arguably inconsistent with a security policy in which a contributor's draft can only be read by editors until published by an editor. NOTE: the vendor's position is that this behavior has no security impact.

## References
- https://ghost.org/docs/security/
- https://gist.github.com/yurahod/2e11eabbe4b92ef1d44b08e37023ecfb
- https://gist.github.com/yurahod/828d5e6a077c12f3f74c6485d1c7f0e7
- https://nvd.nist.gov/vuln/detail/CVE-2023-26510
