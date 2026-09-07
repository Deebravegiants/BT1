# [H] GraphQL query operations security can be bypassed

## Summary
Severity: High
Advisory: GHSA-cg3c-245w-728m
CVE: CVE-2025-31481
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-cg3c-245w-728m
Type: github-advisory

## Affected
- Packagist: `api-platform/graphql` — affected >=4.0.0-alpha.1 <4.0.22
- Packagist: `api-platform/core` — affected >=4.0.0-alpha.1 <4.0.22
- Packagist: `api-platform/graphql` — affected >=0 <3.4.17
- Packagist: `api-platform/core` — affected >=0 <3.4.17
- Packagist: `api-platform/graphql` — affected >=4.1.0-alpha.1 <4.1.5
- Packagist: `api-platform/core` — affected >=4.1.0-alpha.1 <4.1.5

## Details
### Summary

Using the Relay special `node` type you can bypass the configured security on an operation.

### Details

Here is an example of how to apply security configurations for the GraphQL operations:

```php
#[ApiResource(
    security: "is_granted('ROLE_USER')",
    operations: [ /* ... */ ],
    graphQlOperations: [
        new Query(security: "is_granted('ROLE_USER')"),
        //...
    ],
)]
class Book { /* ... */ }
```

This indeed checks `is_granted('ROLE_USER')` as expected for a GraphQL query like the following:

```php
‌query {
    book(id: "/books/1") {
        title
    }
}
```

But the security check can be bypassed by using the `node` field (that is available by default) on the root query type like that:

```php
‌query {
    node(id: "/books/1") {
        ... on Book {
            title
        }
    }
}
```

This does not execute any security checks and can therefore be used to access any entity without restrictions by everyone that has access to the API.

### Impact

Everyone using GraphQl with the `security` attribute. Not sure whereas this works with custom resolvers nor if this also applies on mutation.

Patched at https://github.com/api-platform/core/commit/60747cc8c2fb855798c923b5537888f8d0969568

## References
- https://github.com/api-platform/core/security/advisories/GHSA-cg3c-245w-728m
- https://nvd.nist.gov/vuln/detail/CVE-2025-31481
- https://github.com/api-platform/core/commit/55712452b4f630978537bdb2a07dc958202336bb
- https://github.com/api-platform/core/commit/60747cc8c2fb855798c923b5537888f8d0969568
- https://github.com/FriendsOfPHP/security-advisories/blob/master/api-platform/core/CVE-2025-31481.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/api-platform/graphql/CVE-2025-31481.yaml
- https://github.com/api-platform/core
- https://github.com/api-platform/core/releases/tag/v3.4.17
- https://github.com/api-platform/core/releases/tag/v4.1.5
