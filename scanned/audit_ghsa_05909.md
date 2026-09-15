# [M] API Platform Core: Relation IRIs are not type-checked: a related resource can be denormalised as the wrong resource type (type confusion)

## Summary
Severity: Medium
Advisory: GHSA-9rjg-x2p2-h68h
CVE: CVE-2026-54164
CWE: CWE-843
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-9rjg-x2p2-h68h
Type: github-advisory

## Affected
- Packagist: `api-platform/core` — affected >=0 <4.1.30
- Packagist: `api-platform/core` — affected >=4.2.0 <4.2.26
- Packagist: `api-platform/core` — affected >=4.3.0 <4.3.12

## Details
## Summary

The API Platform serializer's `AbstractItemNormalizer` does not validate the resource type returned when resolving relation IRIs, allowing type confusion where a resource of an unintended type can be silently assigned to a relation property.

## Impact

An attacker who can submit write requests (POST/PUT/PATCH) to an API Platform endpoint with writable relations can supply a relation IRI pointing to a resource of a different type than the relation's declared class. Because `getResourceFromIri()` does not pass an `$operation` to `IriConverter::getResourceFromIri()`, the `is_a` type guard at `IriConverter.php:86` is skipped. For untyped relation properties (legacy `@var`-only style), the wrong-typed object is silently assigned, corrupting invariants and potentially feeding downstream logic that assumes the declared type (CWE-843). For typed properties (modern PHP 8.x), the substitution is blocked by Symfony's PropertyAccessor with an `InvalidTypeException`.

## Affected versions

- `api-platform/core` `< 4.1.30`
- `api-platform/core` `>= 4.2.0, < 4.2.26`
- `api-platform/core` `>= 4.3.0, < 4.3.12`

Older major series (`2.x`, `3.x`) ship the same vulnerable code path and are end-of-life; no fix is planned.

## Patched versions

- `4.1.30`
- `4.2.26`
- `4.3.12`

## Fix

An `is_a` guard is added inside `AbstractItemNormalizer::getResourceFromIri()` (and the equivalent inline call sites on 4.1) so that a mismatched IRI throws `InvalidArgumentException`, mirroring the operation-aware check the `IriConverter` already performs when an operation is supplied. This forces a `400 Bad Request` response for cross-type IRIs instead of a silent assignment.

## Workarounds

Declare a PHP type on every writable relation property (e.g. `public ?Foo $relation = null;` instead of `@var Foo $relation`). Symfony's `PropertyAccessor` will then reject a mismatched object with `InvalidTypeException`. This does not cover collections of mixed-type interfaces; upgrading to a patched version is the only complete fix.

## Proof of concept

A functional test posts a `Bar` IRI to a `Foo`-declared relation on an untyped property. Without the fix the server responds with `HTTP 201` and the Bar IRI appears in the response payload. With the fix the server responds with `HTTP 400` (`Invalid IRI "/bars/1"`).

Full PoC: `tests/Functional/Security/TypeConfusionRelationIriTest.php` in the patched branches.

## References

- `src/Serializer/AbstractItemNormalizer.php` — vulnerable relation IRI load
- `src/Symfony/Routing/IriConverter.php` — conditional `is_a` guard (operation-aware path)

## Credit

Reported by @alexandre-daubois.

## References
- https://github.com/api-platform/core/security/advisories/GHSA-9rjg-x2p2-h68h
- https://nvd.nist.gov/vuln/detail/CVE-2026-54164
- https://github.com/api-platform/core/commit/6bcbeb2dbee53db5bb9b4b8e343bffdf7732de1e
- https://github.com/api-platform/core
- https://github.com/api-platform/core/releases/tag/v4.1.30
- https://github.com/api-platform/core/releases/tag/v4.2.26
- https://github.com/api-platform/core/releases/tag/v4.3.12
