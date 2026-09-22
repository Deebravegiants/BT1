# [H] async-graphql Directive Overload

## Summary
Severity: High
Advisory: GHSA-5gc2-7c65-8fq8
CVE: CVE-2024-47614
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-5gc2-7c65-8fq8
Type: github-advisory

## Affected
- crates.io: `async-graphql` — affected >=0 <7.0.10

## Details
### Impact

- Service Disruption: The server may become unresponsive or extremely slow, potentially leading to downtime.
- Resource Exhaustion: Excessive use of server resources, such as CPU and memory, could negatively impact other services running on the same infrastructure.
- User Experience Degradation: Users may experience delays or failures when accessing the service, which could lead to frustration and loss of trust in the service.

### Patches

1. Upgrade to v7.0.10
2. Use [SchemaBuilder.limit_directives](https://docs.rs/async-graphql/latest/async_graphql/struct.SchemaBuilder.html#method.limit_directives) to limit the maximum number of directives for a single field.

## References
- https://github.com/async-graphql/async-graphql/security/advisories/GHSA-5gc2-7c65-8fq8
- https://nvd.nist.gov/vuln/detail/CVE-2024-47614
- https://github.com/async-graphql/async-graphql/commit/7f1791488463d4e9c5adcd543962173e2f6cbd34
- https://github.com/async-graphql/async-graphql
