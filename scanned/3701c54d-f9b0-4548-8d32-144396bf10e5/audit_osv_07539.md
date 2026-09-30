# [M] SuiteCRM has Unauthenticated Graphql Introspection Enabled

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2023-47643
Aliases: CVE-2023-47643, GHSA-fxww-jqfv-9rrr
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2023-47643
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.4.1 <8.4.2

## Details
SuiteCRM is a Customer Relationship Management (CRM) software application. Prior to version 8.4.2, Graphql Introspection is enabled without authentication, exposing the scheme defining all object types, arguments, and functions. An attacker can obtain the GraphQL schema and understand the entire attack surface of the API, including sensitive fields such as UserHash. This issue is patched in version 8.4.2. There are no known workarounds.

## References
- https://github.com/salesagility/SuiteCRM-Core/commit/117dd8172793a239f71c91222606bf00677eeb33
- https://github.com/salesagility/SuiteCRM-Core/security/advisories/GHSA-fxww-jqfv-9rrr
- https://www.apollographql.com/blog/graphql/security/why-you-should-disable-graphql-introspection-in-production/
- https://nvd.nist.gov/vuln/detail/CVE-2023-47643
