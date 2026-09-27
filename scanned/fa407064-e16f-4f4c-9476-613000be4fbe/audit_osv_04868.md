# [C] BIT-ghost-2024-34451

## Summary
Severity: Critical
Advisory: BIT-ghost-2024-34451
Aliases: CVE-2024-34451
Ecosystem: Bitnami
Published: 2025-06-23
Source: https://osv.dev/vulnerability/BIT-ghost-2024-34451
Type: osv

## Affected
- Bitnami: `ghost` — affected >=0 <5.110.4

## Details
Ghost through 5.85.1 allows remote attackers to bypass an authentication rate-limit protection mechanism by using many X-Forwarded-For headers with different values. NOTE: the vendor's position is that Ghost should be installed with a reverse proxy that allows only trusted X-Forwarded-For headers.

## References
- https://docs.google.com/document/d/1iy0X4Vc9xXYoBxFrcW6ATo8GKPV6ivuLVzn6GgEpwqE
- https://ghost.org/docs/faq/proxying-https-infinite-loops/
- https://github.com/TryGhost/Ghost/releases
- https://nvd.nist.gov/vuln/detail/CVE-2024-34451
