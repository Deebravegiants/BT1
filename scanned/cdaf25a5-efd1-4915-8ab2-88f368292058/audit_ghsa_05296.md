# [M] ux-live-component: Format-less date LiveProps parsed with the permissive DateTime constructor

## Summary
Severity: Medium
Advisory: GHSA-89g7-22c8-3j23
CVE: CVE-2026-49208
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-89g7-22c8-3j23
Type: github-advisory

## Affected
- Packagist: `symfony/ux-live-component` — affected >=2.8.0 <2.36.0
- Packagist: `symfony/ux-live-component` — affected >=3.0.0 <3.1.0

## Details
### Description

When a `#[LiveProp]` is typed as a `DateTimeInterface` and no explicit `format` is configured, `Symfony\UX\LiveComponent\LiveComponentHydrator::hydrateObjectValue()` falls back to `new $className($value)`. The `DateTime` / `DateTimeImmutable` constructors accept relative strings such as `"now"`, `"tomorrow"`, or `"+10 years"`, so a writable, format-less date prop can be pushed to an arbitrary point in time by the client. Components that rely on a date prop to gate time-based business logic can be moved past those checks by a frontend payload that no maintainer would consider a valid date.

### Resolution

`hydrateObjectValue()` now parses format-less date props strictly with `createFromFormat(DateTimeInterface::RFC3339, ...)`, matching the format already emitted by `dehydrateObjectValue()`. Normal round-trips are unaffected; only inputs that aren't valid RFC 3339 are now rejected, which is consistent with how a format-configured prop already behaved.

The patch for this issue is available [here](https://github.com/symfony/ux/commit/d24d78fda6df2d5964312255943ebf3a217b79a2) for branch 2.x (and forward-ported to 3.x).

### Credits

Symfony would like to thank Pascal Cescon for reporting the issue and Hugo Alliaume for providing the fix.

## References
- https://github.com/symfony/ux/security/advisories/GHSA-89g7-22c8-3j23
- https://github.com/symfony/ux/commit/d24d78fda6df2d5964312255943ebf3a217b79a2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/ux-live-component/CVE-2026-49208.yaml
- https://github.com/symfony/ux
