# [M] nova-toggle-5: Improper authorization on toggle endpoint allowed non-Nova users to modify boolean fields

## Summary
Severity: Medium
Advisory: GHSA-f5c8-m5vw-rmgq
CVE: CVE-2026-42202
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-f5c8-m5vw-rmgq
Type: github-advisory

## Affected
- Packagist: `almirhodzic/nova-toggle-5` — affected >=0 <1.3.0

## Details
### Impact

In versions `< 1.3.0`, the toggle endpoint (`POST /nova-vendor/nova-toggle/toggle/{resource}/{resourceId}`) was protected only by `web` + `auth:<guard>` middleware. Any user authenticated on the configured guard could call the endpoint and flip boolean attributes on any Nova resource — including users who do not have access to Nova itself (for example, frontend customers sharing the `web` guard with the Nova admin area).

The endpoint also accepted an arbitrary `attribute` parameter, which meant a valid caller could toggle any boolean column on the underlying model — not just columns exposed as `Toggle` fields on the resource.

### Patches

Fixed in `1.3.0`:

- The route is now protected by Nova's `nova:api` middleware, which enforces the `viewNova` gate.
- The controller now checks the resource's `authorizedToUpdate` policy.
- The controller only accepts attributes that are declared as a `Toggle` field on the resource and are not readonly in the current request context.

### Workarounds

Users who cannot upgrade immediately can either remove the package or restrict access to the `/nova-vendor/nova-toggle/toggle/*` routes via an additional middleware in their application that enforces the `viewNova` gate.

### Credits

nova-toggle-5 thanks [Roberto Negro](https://github.com/RobertoNegro) for the responsible disclosure.

## References
- https://github.com/almirhodzic/nova-toggle-5/security/advisories/GHSA-f5c8-m5vw-rmgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42202
- https://github.com/almirhodzic/nova-toggle-5
- https://github.com/almirhodzic/nova-toggle-5/blob/main/CHANGELOG.md
- https://github.com/almirhodzic/nova-toggle-5/releases/tag/v1.3.0
