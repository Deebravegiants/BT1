# [C] Strapi Vulnerable to SQL Injection in Content Type Builder

## Summary
Severity: Critical
Advisory: GHSA-3xcq-8mjw-h6mx
CVE: CVE-2026-22599
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-3xcq-8mjw-h6mx
Type: github-advisory

## Affected
- npm: `@strapi/content-type-builder` — affected >=5.0.0 <5.33.2
- npm: `@strapi/plugin-content-type-builder` — affected >=4.0.0 <4.26.1

## Details
### Summary of CVE-2026-22599 Vulnerability Details

- CVE: CVE-2026-22599
- CVSS v3.1 Vector: `CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N` (9.3 — Critical)
- Affected Versions: `@strapi/content-type-builder` <=5.33.1 (v5), `@strapi/plugin-content-type-builder` <=4.26.0 (v4)
- How to Patch: Immediately update your Strapi to >=5.33.2 (v5) or >=4.26.1 (v4)

### Description of CVE-2026-22599

A database-query injection vulnerability existed in the Strapi Content-Type Builder write API. An authenticated administrator could inject arbitrary database statements through the `column.defaultTo` attribute when creating or modifying a content type. Setting `defaultTo` as a tuple `[value, { isRaw: true }]` caused the value to be passed directly into Knex's `db.connection.raw()` during schema migration without sanitization, allowing arbitrary statement execution at the database layer. Depending on the database engine, this enabled arbitrary file read via database utility functions, denial of service via forced server crash on schema-migration error, and on engines that permit external program execution, remote code execution against the database server.

The patch addresses this by restricting all Content-Type Builder write APIs to development mode only. Production deployments running v5.33.2 or later return 404 for requests against `/content-type-builder/content-types` and related endpoints, removing the network-reachable attack surface entirely.

### IoC's for CVE-2026-22599

Indicators that an instance running an unpatched version may have been exploited:

- HTTP access logs containing POST or PUT requests to `/content-type-builder/content-types` from a non-internal source. Regex pattern: `(POST|PUT)\s+/content-type-builder/`
- Database server logs containing unexpected DEFAULT clause values that reference filesystem-access or program-execution helper functions of your database engine
- Strapi server crashes immediately following a content-type creation or update, observed as the Node process exiting during the schema-migration step
- Files appearing under unexpected paths on the database host that match content-type DEFAULT values from the application
- Newly-created content-types named or shaped to extract specific data (attribute names like `passwd`, `etc`, `env`, `config`)

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-3xcq-8mjw-h6mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-22599
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v4.26.1
- https://github.com/strapi/strapi/releases/tag/v5.33.2
