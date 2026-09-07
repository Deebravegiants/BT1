# [M] Directus: GraphQL Schema SDL Disclosure Setting

## Summary
Severity: Medium
Advisory: GHSA-wxwm-3fxv-mrvx
CVE: CVE-2026-35413
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-wxwm-3fxv-mrvx
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.16.1

## Details
## Summary

When `GRAPHQL_INTROSPECTION=false` is configured, Directus correctly blocks standard GraphQL introspection queries (`__schema`, `__type`). However, the `server_specs_graphql` resolver on the `/graphql/system` endpoint returns an equivalent SDL representation of the schema and was not subject to the same restriction. This allowed the introspection control to be bypassed, exposing schema structure (collection names, field names, types, and relationships) to unauthenticated users at the public permission level, and to authenticated users at their permitted permission level.

## Impact

Administrators who set `GRAPHQL_INTROSPECTION=false` to hide schema structure from clients would have had a false sense of security, as equivalent schema information remained accessible via the SDL endpoint without authentication.

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/directus/directus/security/advisories/GHSA-wxwm-3fxv-mrvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-35413
- https://github.com/directus/directus
