# [M] Sulu: Media move/update authorization bypass (IDOR)

## Summary
Severity: Medium
Advisory: GHSA-h6cx-gjxx-v25c
CVE: CVE-2026-82395
CWE: CWE-639, CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-h6cx-gjxx-v25c
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=0 <2.6.25
- Packagist: `sulu/sulu` — affected >=3.0.0-alpha1 <3.0.8

## Details
### Impact

A media move authorization bypass (IDOR) lets a backend user move a media out of a collection they have no access to.

The media move endpoint resolves its permission check from the `collection` value in the request rather than from the media's real collection. `MediaManager::move()` then reassigns the media without re-checking its actual source collection. A user who has edit rights on collection A but no rights on a restricted collection B can move a media that lives in B by naming A in the request. The move succeeds, the media ends up in A, and the user can then view and download content they were never allowed to see.

This only affects installations that use per-collection (object level) permissions to restrict some collections. Exploitation requires an authenticated backend user with edit rights on at least one collection, and knowledge of the target media id.

### Patches

Fixed in **2.6.25** and **3.0.8**. `MediaManager::move()` now verifies edit permission on the media's real source collection and on the destination collection before moving it.

### Workarounds

If you cannot upgrade immediately:

- Restrict the media edit permission to trusted users, so untrusted users cannot trigger a move.
- Apply the fix manually by adding an edit permission check on the media's real source collection (and the destination) inside `MediaManager::move()`.

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-h6cx-gjxx-v25c
- https://nvd.nist.gov/vuln/detail/CVE-2026-82395
- https://github.com/sulu/sulu/commit/2b959de75d61b98433e42db462c246ed9e4ce793
- https://github.com/sulu/sulu
- https://github.com/sulu/sulu/releases/tag/2.6.25
- https://github.com/sulu/sulu/releases/tag/3.0.8
