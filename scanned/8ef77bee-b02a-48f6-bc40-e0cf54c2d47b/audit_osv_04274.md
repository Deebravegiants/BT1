# [H] cert-manager: Direct ACME Challenge resources can bypass Issuer DNS01 solver policy and use ClusterIssuer DNS credentials

## Summary
Severity: High
Advisory: BIT-cert-manager-2026-62290
Aliases: CVE-2026-62290, GHSA-8rvj-mm4h-c258
Ecosystem: Bitnami
Published: 2026-07-27
Source: https://osv.dev/vulnerability/BIT-cert-manager-2026-62290
Type: osv

## Affected
- Bitnami: `cert-manager` — affected >=1.20.0 <1.20.3

## Details
cert-manager adds certificates and certificate issuers as resource types in Kubernetes clusters, and simplifies the process of obtaining, renewing and using those certificates. From 1.18.0 until 1.19.6 and 1.20.3, Challenge resources under acme.cert-manager.io can be created directly by namespace users without admission validation tying the Challenge to an Order, owner reference, or Issuer-selected solver, allowing attacker-controlled Challenge.spec.solver values referencing a ClusterIssuer to bypass DNS01 solver selectors such as dnsZones, dnsNames, and matchLabels and cause cert-manager to use ClusterIssuer DNS credentials for attacker-selected provider settings and DNS names, including disclosure of X-Api-User and X-Api-Key headers for acme-dns. This issue is fixed in versions 1.19.6 and 1.20.3.

## References
- https://github.com/cert-manager/cert-manager/commit/6bda47297c8fbc6b121b8b76624b668d26f1a155
- https://github.com/cert-manager/cert-manager/commit/b37dbf01ecea50a0b3a19df0a7fe4c5ad6803f16
- https://github.com/cert-manager/cert-manager/pull/8940
- https://github.com/cert-manager/cert-manager/pull/8941
- https://github.com/cert-manager/cert-manager/releases/tag/v1.19.6
- https://github.com/cert-manager/cert-manager/releases/tag/v1.20.3
- https://github.com/cert-manager/cert-manager/security/advisories/GHSA-8rvj-mm4h-c258
- https://nvd.nist.gov/vuln/detail/CVE-2026-62290
