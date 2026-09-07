# [C] Apollo Federation vulnerable to prototype pollution via incomplete key sanitization

## Summary
Severity: Critical
Advisory: GHSA-pfjj-6f4p-rvmh
CVE: CVE-2026-32621
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-pfjj-6f4p-rvmh
Type: github-advisory

## Affected
- npm: `@apollo/federation-internals` — affected >=0 <2.9.6
- npm: `@apollo/federation-internals` — affected >=2.10.0 <2.10.5
- npm: `@apollo/federation-internals` — affected >=2.11.0 <2.11.6
- npm: `@apollo/federation-internals` — affected >=2.12.0 <2.12.3
- npm: `@apollo/federation-internals` — affected >=2.13.0 <2.13.2
- npm: `@apollo/gateway` — affected >=0 <2.9.6
- npm: `@apollo/gateway` — affected >=2.10.0 <2.10.5
- npm: `@apollo/gateway` — affected >=2.11.0 <2.11.6
- npm: `@apollo/gateway` — affected >=2.12.0 <2.12.3
- npm: `@apollo/gateway` — affected >=2.13.0 <2.13.2
- npm: `@apollo/query-planner` — affected >=0 <2.9.6
- npm: `@apollo/query-planner` — affected >=2.10.0 <2.10.5
- npm: `@apollo/query-planner` — affected >=2.11.0 <2.11.6
- npm: `@apollo/query-planner` — affected >=2.12.0 <2.12.3
- npm: `@apollo/query-planner` — affected >=2.13.0 <2.13.2

## Details
### Impact

A vulnerability exists in query plan execution within the gateway that may allow pollution of `Object.prototype` in certain scenarios. A malicious client may be able to pollute `Object.prototype` in gateway directly by crafting operations with field aliases and/or variable names that target prototype-inheritable properties. Alternatively, if a subgraph were to be compromised by a malicious actor, they may be able to pollute `Object.prototype` in gateway by crafting JSON response payloads that target prototype-inheritable properties.

Because `Object.prototype` is shared across the Node.js process, successful exploitation can affect subsequent requests to the gateway instance. This may result in unexpected application behavior, privilege escalation, data integrity issues, or other security impact depending on how polluted properties are subsequently consumed by the application or its dependencies. As of the date of this advisory, Apollo is not aware of any reported exploitation of this vulnerability.

### Patches
Mitigations addressing prototype pollution exposure have been applied in `@apollo/federation-internals`, `@apollo/gateway`, and `@apollo/query-planner` versions `2.9.6`, `2.10.5`, `2.11.6`, `2.12.3`, and `2.13.2`.   Users are encouraged to upgrade to these versions or later at their earliest convenience.

### Workarounds
A fully effective workaround is not available without a code change. As an interim measure, users who are unable to upgrade immediately may consider placing an input validation layer in front of the gateway to filter operations containing [GraphQL names](https://spec.graphql.org/September2025/#sec-Names) matching known `Object.prototype` pollution patterns (e.g., `__proto__`, `constructor`, `prototype`). Users should also ensure that subgraphs in their federated graph originate from trusted sources.

## References
- https://github.com/apollographql/federation/security/advisories/GHSA-pfjj-6f4p-rvmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-32621
- https://github.com/apollographql/federation
