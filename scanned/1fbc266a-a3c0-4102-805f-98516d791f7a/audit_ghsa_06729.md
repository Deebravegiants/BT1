# [M] API Platform Core vulnerable to cross-user attribute leak in JSON:API and HAL item normalizers due to missing isCacheKeySafe gate

## Summary
Severity: Medium
Advisory: GHSA-pjhx-3c3w-9v23
CVE: CVE-2026-49858
CWE: CWE-524, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-pjhx-3c3w-9v23
Type: github-advisory

## Affected
- Packagist: `api-platform/core` — affected >=2.6.0 <4.1.29
- Packagist: `api-platform/core` — affected >=4.2.0 <4.2.25
- Packagist: `api-platform/core` — affected >=4.3.0 <4.3.8
- Packagist: `api-platform/json-api` — affected >=4.0.0 <4.1.29
- Packagist: `api-platform/json-api` — affected >=4.2.0 <4.2.25
- Packagist: `api-platform/json-api` — affected >=4.3.0 <4.3.8
- Packagist: `api-platform/hal` — affected >=4.0.0 <4.1.29
- Packagist: `api-platform/hal` — affected >=4.2.0 <4.2.25
- Packagist: `api-platform/hal` — affected >=4.3.0 <4.3.8

## Details
### Impact

`#[ApiProperty(security: ...)]` is evaluated per request to decide whether a property is exposed. The `componentsCache` arrays in `ApiPlatform\JsonApi\Serializer\ItemNormalizer` and `ApiPlatform\Hal\Serializer\ItemNormalizer` are keyed on `$context['cache_key']`, which is set unconditionally before delegating to the parent normalizer. The component structure (attributes, relationships, links) computed for one request can therefore be reused for a subsequent request whose user has a different set of accessible properties. A user with lower privileges may end up seeing the structure of properties that the security predicate would otherwise have hidden for them.

This is the same vulnerability class as [GHSA-428q-q3vv-3fq3](https://github.com/api-platform/core/security/advisories/GHSA-428q-q3vv-3fq3) / CVE-2025-31485, which fixed only the GraphQL `ItemNormalizer`. The JSON:API and HAL paths were not addressed at the time.

### Exploitation conditions

Exploitation requires all of the following to coincide:

- The application exposes a resource via the JSON:API and/or HAL formats.
- At least one property of that resource uses `#[ApiProperty(security: ...)]` with a predicate whose result depends on the current user (or on per-request state).
- A request from a user for whom the predicate evaluates to `true` populates `componentsCache` before a request from a user for whom the predicate evaluates to `false`, within the lifetime of the same PHP process.
- The deployment uses a long-running PHP runtime that keeps the normalizer instance alive across requests (FrankenPHP worker mode, RoadRunner, Swoole, ReactPHP, etc.). With classic `php-fpm` workers the cache only survives the duration of a single request, which makes the issue much harder to observe in practice.

### Patches

- 4.1.29
- 4.2.25
- 4.3.8

All three branches receive patched releases of `api-platform/core`, `api-platform/json-api`, and `api-platform/hal`.

### Workarounds

Override the JSON:API and HAL `ItemNormalizer` services to gate `$context['cache_key']` with a resource-class security check, or avoid `#[ApiProperty(security: ...)]` on resources served as JSON:API or HAL until the patch is applied. Pinning the deployment to classic `php-fpm` workers also limits exposure since the cache does not survive across requests.

### Credits

- Tillmann Baumgart (@tillmon) — originally identified the broader cache-key gap and proposed moving `isCacheKeySafe` to `AbstractItemNormalizer`.
- Antoine Bluchet (@soyuka) — extended the gate to JSON:API and HAL normalizers.

## References
- https://github.com/api-platform/core/security/advisories/GHSA-pjhx-3c3w-9v23
- https://nvd.nist.gov/vuln/detail/CVE-2026-49858
- https://github.com/api-platform/core
