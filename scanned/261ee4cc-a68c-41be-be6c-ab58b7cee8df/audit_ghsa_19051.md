# [H] @apollo/composition has Improper Enforcement of Access Control on Interface Types and Fields

## Summary
Severity: High
Advisory: GHSA-mx7m-j9xf-62hw
CVE: CVE-2025-64530
CWE: CWE-284, CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-mx7m-j9xf-62hw
Type: github-advisory

## Affected
- npm: `@apollo/composition` — affected >=0 <2.9.5
- npm: `@apollo/composition` — affected >=2.10.0-alpha.3 <2.10.4
- npm: `@apollo/composition` — affected >=2.11.0-preview.1 <2.11.5
- npm: `@apollo/composition` — affected >=2.12.0-preview.1 <2.12.1

## Details
# Summary
A vulnerability in Apollo Federation's composition logic allowed some queries to Apollo Router to improperly bypass access controls on types/fields. Apollo Federation incorrectly allowed user-defined access control directives on interface types/fields, which could be bypassed by instead querying the implementing object types/fields in Apollo Router via inline or named fragments. A fix to composition logic in Federation now disallows interfaces types and fields to contain user-defined access control directives.

## Details
Apollo Federation allows users to specify access control directives ([`@authenticated`, `@requiresScopes`, and `@policy`](https://www.apollographql.com/docs/graphos/routing/security/authorization#authorization-directives)) to protect object and interface types and fields. However, the GraphQL specification does not define inheritance rules for directives from interfaces to their implementations. When querying object or interface types/fields, Apollo Router will enforce any directives on those object or interface types/fields, but ignore any directives on interface types/fields they implement. This inconsistent enforcement behavior leads to unexpected runtime security gaps.

## Who is impacted
This vulnerability impacts Apollo Federation customers defining `@authenticated`, `@requiresScopes`, or `@policy` directives on interface types/fields.

### Scope of Impact
This vulnerability could allow a malicious actor to craft a query that can bypass access control requirements on the interface types/fields by instead querying them via implementing object types/fields that don't have the same access control requirements via inline or named fragments.

## Patches
This vulnerability has been fixed in Apollo Federation's composition logic by rejecting user-defined access control directives entirely on interface types and fields (note that access control directives on `@interfaceObject` fields are not rejected, as those are really specifying requirements on the virtual object fields). Instead, Apollo Federation's composition logic will automatically generate access control directives for interface types/fields in the supergraph schema based on the access control directives on the implementations in subgraph schemas. 

_Note that this is a breaking change to Apollo Federation, as it no longer allows user-defined access control directives directly on interfaces types and fields. You will need to remove all access control requirements on interface types/fields and manually apply them to each implementing object type/field, where appropriate._

If users are using the Apollo Studio build pipeline with federation version 2.9 or above, then this composition patch version update is automatic and they only need to adjust the access control requirements in your subgraph schemas as mentioned above.

If users are using Apollo Rover for local composition, they will need to update its composition version (after updating Apollo Router, [if necessary](https://www.apollographql.com/docs/graphos/platform/graph-management/updates#recommended-update-order)) to one of the following versions:

- 2.9.5+
- 2.10.4+
- 2.11.5+
- 2.12.1+

Users will then need adjust the access control requirements in your subgraph schemas as mentioned above.

## Workarounds
- If using Apollo Rover with an unpatched composition version or are using the Apollo Studio build pipeline with Federation version 2.8 or below, users should manually copy the access control requirements on interface types/fields to each implementing object type/field where appropriate. _Do not_ remove those access control requirements from the interface types/fields, as unpatched Apollo Composition will not automatically generate them in the supergraph schema.
- Customers not using Apollo Router access control features (`@authenticated`, `@requiresScopes`, or `@policy` directives) or not specifying access control requirements on interface types/fields are not affected and do not need to take action.

## References
- https://github.com/apollographql/federation/security/advisories/GHSA-mx7m-j9xf-62hw
- https://nvd.nist.gov/vuln/detail/CVE-2025-64530
- https://github.com/apollographql/federation/pull/3340
- https://github.com/apollographql/federation/pull/3341
- https://github.com/apollographql/federation/pull/3343
- https://github.com/apollographql/federation
