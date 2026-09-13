# [C] @vendure/core has a SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9pp3-53p2-ww9v
CVE: CVE-2026-40887
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-9pp3-53p2-ww9v
Type: github-advisory

## Affected
- npm: `@vendure/core` — affected >=3.0.0 <3.5.7
- npm: `@vendure/core` — affected >=3.6.0 <3.6.2
- npm: `@vendure/core` — affected >=1.7.4 <2.3.4

## Details
## Summary

An unauthenticated SQL injection vulnerability exists in the Vendure Shop API. A user-controlled query string parameter is interpolated directly into a raw SQL expression without parameterization or validation, allowing an attacker to execute arbitrary SQL against the database. This affects all supported database backends (PostgreSQL, MySQL/MariaDB, SQLite).

The Admin API is also affected, though exploitation there requires authentication.

## Affected versions

- `@vendure/core` < 2.3.4
- `@vendure/core` >= 3.0.0, < 3.5.7
- `@vendure/core` >= 3.6.0, < 3.6.2

Note: versions 2.3.4 and above in the 2.x line are patched. There were no 2.4.x or 2.x releases between 2.3.x and 3.0.0.

## Patched versions

- `@vendure/core` 2.3.4
- `@vendure/core` 3.5.7
- `@vendure/core` 3.6.2

## Details

In `ProductService.findOneBySlug`, the request context's `languageCode` value is interpolated into a SQL `CASE` expression via a JavaScript template literal:

```ts
.addSelect(
    `CASE translation.languageCode WHEN '${ctx.languageCode}' THEN 2 WHEN '${ctx.channel.defaultLanguageCode}' THEN 1 ELSE 0 END`,
    'sort_order',
)
```

TypeORM has no opportunity to parameterize this value because it is embedded directly into the SQL string before being passed to the query builder.

The `languageCode` value can originate from the HTTP query string and is set on the request context for every incoming API request. The value is cast to the `LanguageCode` TypeScript type at compile time, but no runtime validation is performed -- the raw query string value is used as-is.

## Attack vector

An unauthenticated attacker can append a crafted `languageCode` query parameter to any Shop API request to inject arbitrary SQL into the query. No user interaction is required. The vulnerable endpoint is exposed on every default Vendure installation.

## Mitigation

**Upgrade to a patched version immediately.**

If you cannot upgrade right away, apply the following hotfix to `RequestContextService.getLanguageCode` to validate the `languageCode` input at the boundary. This blocks injection payloads before they can reach any query:

```ts
private getLanguageCode(req: Request, channel: Channel): LanguageCode | undefined {
    const queryLanguageCode = req.query?.languageCode as string | undefined;
    const isValidFormat = queryLanguageCode && /^[a-zA-Z0-9_-]+$/.test(queryLanguageCode);
    return (
        (isValidFormat ? (queryLanguageCode as LanguageCode) : undefined) ??
        channel.defaultLanguageCode ??
        this.configService.defaultLanguageCode
    );
}
```

This replaces the existing `getLanguageCode` method in `packages/core/src/service/helpers/request-context/request-context.service.ts`. Invalid values are silently dropped and the channel's default language is used instead.

The patched versions additionally convert the vulnerable SQL interpolation to a parameterized query as defense in depth.

## References
- https://github.com/vendurehq/vendure/security/advisories/GHSA-9pp3-53p2-ww9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-40887
- https://github.com/vendurehq/vendure
