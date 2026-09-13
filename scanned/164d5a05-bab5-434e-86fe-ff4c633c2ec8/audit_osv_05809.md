# [M] BIT-harbor-2020-13788

## Summary
Severity: Medium
Advisory: BIT-harbor-2020-13788
Aliases: CVE-2020-13788, GHSA-33p6-fx42-7rf5, GO-2022-0781
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-harbor-2020-13788
Type: osv

## Affected
- Bitnami: `harbor` — affected >=0 <2.0.1

## Details
Harbor prior to 2.0.1 allows SSRF with this limitation: an attacker with the ability to edit projects can scan ports of hosts accessible on the Harbor server's intranet.

## References
- https://github.com/goharbor/harbor/releases
- https://www.soluble.ai/blog/harbor-ssrf-cve-2020-13788
- https://www.youtube.com/watch?v=v8Isqy4yR3Q
- https://nvd.nist.gov/vuln/detail/CVE-2020-13788
