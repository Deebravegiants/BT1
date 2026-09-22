# [M] BIT-argo-cd-2021-26921

## Summary
Severity: Medium
Advisory: BIT-argo-cd-2021-26921
Aliases: CVE-2021-26921, GHSA-9h6w-j7w4-jr52
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-argo-cd-2021-26921
Type: osv

## Affected
- Bitnami: `argo-cd` — affected >=1.8.0 <1.8.4

## Details
In util/session/sessionmanager.go in Argo CD before 1.8.4, tokens continue to work even when the user account is disabled.

## References
- https://github.com/argoproj/argo-cd/commit/f5b0db240b4e3abf18e97f6fd99096b4f9e94dc5
- https://github.com/argoproj/argo-cd/compare/v1.8.3...v1.8.4
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-9h6w-j7w4-jr52
