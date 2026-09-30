# [C] Auth misconfiguration when multiple providers enabled

## Summary
Severity: Critical
Advisory: BIT-neo4j-2026-1524
Aliases: BIT-neo4j-enterprise-2026-1524, CVE-2026-1524
Ecosystem: Bitnami
Published: 2026-05-29
Source: https://osv.dev/vulnerability/BIT-neo4j-2026-1524
Type: osv

## Affected
- Bitnami: `neo4j` — affected >=2025.1.0 <2026.2.0

## Details
An edgecase in SSO implementation in Neo4j Enterprise edition versions prior to version 2026.02 can lead to unauthorised access under the following conditions:


If a neo4j admin configures two or more OIDC providers AND configures one or more of them to be an authorization provider AND configures one or more of them to be authentication-only, then those that are authentication-only will also provide authorization. This edgecase becomes a security problem only if the authentication-only provider contains groups which have higher privileges than provided by the intended (configured) authorization provider. 

When using multiple plugins for authentication and authorisation, prior to the fix the issue could lead to a plugin configured to provide only authentication or authorisation capabilities erroneously providing both capabilities. 

We recommend upgrading to versions 2026.02 (or 5.26.22) where the issue is fixed.

## References
- https://neo4j.com/security/CVE-2026-1524
- https://nvd.nist.gov/vuln/detail/CVE-2026-1524
