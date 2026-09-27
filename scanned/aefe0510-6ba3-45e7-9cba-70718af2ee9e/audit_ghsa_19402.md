# [H] GraphQL grant on a property might be cached with different objects

## Summary
Severity: High
Advisory: GHSA-428q-q3vv-3fq3
CVE: CVE-2025-31485
CWE: CWE-696
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-428q-q3vv-3fq3
Type: github-advisory

## Affected
- Packagist: `api-platform/graphql` — affected >=4.0.0-alpha.1 <4.0.22
- Packagist: `api-platform/core` — affected >=4.0.0-alpha.1 <4.0.22
- Packagist: `api-platform/graphql` — affected >=0 <3.4.17
- Packagist: `api-platform/core` — affected >=0 <3.4.17
- Packagist: `api-platform/core` — affected >=4.1.0-alpha.1 <4.1.5
- Packagist: `api-platform/graphql` — affected >=4.1.0-alpha.1 <4.1.5

## Details
### Original message:

I found an issue with security grants on on properties in the GraphQL ItemNormalizer:

If you use something like `#[ApiProperty(security: 'is_granted("PROPERTY_READ", [object, property])')]` on a member of an entity, the grant gets cached and is only evaluated once, even if the `object` in question is a different one.

There is the `ApiPlatform\GraphQl\Serializer\ItemNormalizer::isCacheKeySafe()` method that seems to be intended to prevent this: https://github.com/api-platform/core/blob/88f5ac50d20d6510686a7552310cc567fcca45bf/src/GraphQl/Serializer/ItemNormalizer.php#L160-L164  
and in its usage on line 90 it does indeed not create a cache key, but the `parent::normalize()` that is called afterwards still creates the cache key and causes the issue.

### Impact

It grants access to properties that it should not.

### Workarounds

Override the ItemNormalizer.

Patched at: https://github.com/api-platform/core/commit/7af65aad13037d7649348ee3dcd88e084ef771f8

## References
- https://github.com/api-platform/core/security/advisories/GHSA-428q-q3vv-3fq3
- https://nvd.nist.gov/vuln/detail/CVE-2025-31485
- https://github.com/api-platform/core/commit/7af65aad13037d7649348ee3dcd88e084ef771f8
- https://github.com/api-platform/core/commit/cba3acfbd517763cf320167250c5bed6d569696a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/api-platform/core/CVE-2025-31485.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/api-platform/graphql/CVE-2025-31485.yaml
- https://github.com/api-platform/core
- https://github.com/api-platform/core/releases/tag/v3.4.17
