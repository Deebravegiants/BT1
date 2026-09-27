# [H] BIT-argo-cd-2020-8826

## Summary
Severity: High
Advisory: BIT-argo-cd-2020-8826
Aliases: CVE-2020-8826
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-argo-cd-2020-8826
Type: osv

## Affected
- Bitnami: `argo-cd` — affected >=0 <1.5.0

## Details
As of v1.5.0, the Argo web interface authentication system issued immutable tokens. Authentication tokens, once issued, were usable forever without expiration—there was no refresh or forced re-authentication.

## References
- https://argoproj.github.io/argo-cd/security_considerations/
- https://github.com/argoproj/argo/releases
- https://www.soluble.ai/blog/argo-cves-2020
