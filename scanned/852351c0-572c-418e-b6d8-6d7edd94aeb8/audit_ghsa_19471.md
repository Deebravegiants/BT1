# [H] crud-query-parser SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-9r25-rp3p-h2w4
CVE: CVE-2025-32020
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-9r25-rp3p-h2w4
Type: github-advisory

## Affected
- npm: `crud-query-parser` — affected >=0 <0.1.0

## Details
### Impact

Improper neutralization of the `order`/`sort` parameter in the TypeORM adapter, which allows SQL injection.

You are impacted by this vulnerability if you are using the TypeORM adapter, ordering is enabled and you have not set-up a property filter.

Versions 0.0.1, 0.0.2 and 0.0.3 are affected by this vulnerability.

### Patches

This vulnerability has been fixed in version 0.1.0 and newer, which introduces TypeORM field validation (enabled by default).

### Workarounds

#### Add an allowlist of fields
List all valid fields and use the `filterProperties` function to filter out invalid fields before passing the crudRequest to the `TypeOrmQueryAdapter`. Here's an example:
```ts
crudRequest = filterProperties(crudRequest, ['id', 'title', 'category.name']);
```

#### Disable ordering
Cleanup the `order` field just before passing it to the `TypeOrmQueryAdapter`. Here's an example:
```ts
crudRequest.order = [];
```

## References
- https://github.com/Guichaguri/crud-query-parser/security/advisories/GHSA-9r25-rp3p-h2w4
- https://nvd.nist.gov/vuln/detail/CVE-2025-32020
- https://github.com/Guichaguri/crud-query-parser
