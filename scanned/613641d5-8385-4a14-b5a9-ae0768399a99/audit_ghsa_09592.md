# [M] Gramps Web API: Private Sub-Object Data in Non-Private Objects Exposed to Guest Users

## Summary
Severity: Medium
Advisory: GHSA-9gjv-jvm7-vv2v
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-9gjv-jvm7-vv2v
Type: github-advisory

## Affected
- PyPI: `gramps-webapi` — affected >=0 <3.11.0

## Details
## Summary

Users with the **Guest** role could receive private sub-object data (e.g. private alternate names, private addresses, private note/citation/media handles) through list API endpoints such as `GET /api/people/`, `GET /api/places/`, `GET /api/events/`, and all other object list endpoints.

**This does not expose objects (people, places, events, …) that are themselves marked private.** Top-level private objects are correctly excluded from all responses. Only sub-object data attached to otherwise-public objects is affected.

## Affected Versions

All versions of Gramps Web API prior to the fix.

## Root Cause

The vulnerability originates from the behaviour of `PrivateProxyDb.iter_*()` in **Gramps core**. The `ProxyDbBase.__iter_object()` helper, which backs all `iter_*()` methods in `PrivateProxyDb`, correctly filters out top-level private objects but returns the remaining objects **unsanitized** — i.e. without stripping private sub-object references. In contrast, `PrivateProxyDb.get_*_from_handle()` does call the appropriate `sanitize_*()` function.

Gramps Web API's `ModifiedPrivateProxyDb` (which wraps the raw database for non-admin users) inherited this behaviour without override.

The same issue affects Gramps desktop features that consume `iter_*()` output: reports and exports generated via Gramps desktop using `PrivateProxyDb` may also include private sub-object data that should have been stripped.

## Conditions Required

**This issue only affects trees in which sub-objects have been explicitly marked private in Gramps desktop.** The Gramps Web frontend UI does not expose controls for setting the private flag on sub-objects (alternate names, addresses, notes,
citations, media references, event references, etc.). In practice, such flags are set in Gramps desktop and then synced or imported into Gramps Web.

## Impact

When the conditions above are met, a user with the Guest role querying any list endpoint receives:

- **Full content** of private embedded sub-objects on people, such as alternate  names (first name, surname, etc.) and addresses (street, city, etc.).
- **Handles referencing** private notes, citations, and media attached to places,  events, sources, and other objects. These reveal the *existence* of private
  linked objects but not their content; fetching those objects by handle is  correctly blocked by the proxy.

## Fix

`ModifiedPrivateProxyDb` now overrides all `iter_*()` object methods to check `obj.get_privacy()` directly on the already-loaded object (eliminating the redundant per-object refetch) and to call the appropriate `sanitize_*()` function before yielding each object. This is consistent with the behaviour of `get_*_from_handle()` in `PrivateProxyDb`.

## References
- https://github.com/gramps-project/gramps-web-api/security/advisories/GHSA-9gjv-jvm7-vv2v
- https://github.com/gramps-project/gramps-web-api
- https://github.com/gramps-project/gramps-web-api/releases/tag/v3.11.0
