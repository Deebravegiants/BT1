# [M] Sulu: Fix authorization bypass when creating preview links

## Summary
Severity: Medium
Advisory: GHSA-65cv-w493-7vhq
CVE: CVE-2026-82394
CWE: CWE-862, CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-65cv-w493-7vhq
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=0 <2.6.25
- Packagist: `sulu/sulu` — affected >=3.0.0-alpha1 <3.0.8

## Details
### Impact

A missing authorization check on the preview link endpoint lets a backend user create a public, unauthenticated preview URL for content they are not allowed to see.

`PreviewLinkController` (and the underlying `PreviewLinkManager::generate()` / `revoke()`) never enforced a permission on the target resource. Any authenticated administration user could call the generate action for any page, article or snippet, including content in a webspace or area they have no VIEW rights on. The endpoint returns a public render URL that resolves the content solely by an opaque token, so the attacker (or anyone they share the link with) can then read the restricted content without authentication.

This affects installations that use Sulu role and webspace permissions to restrict who may see certain content. Exploitation requires an authenticated backend user and the id of the target resource.

### Patches

Fixed in **2.6.x** and **3.0.x**. `PreviewLinkManager::generate()` and `revoke()` now resolve the resource's security context and enforce a VIEW permission check before a preview link is created or removed. A user without VIEW access on the resource receives a 403 response and no link is created.

Note on scope: this patch closes the authorization bypass. Two related hardening items from the original report are tracked as a separate follow-up because they require a database migration:

- The preview link token is derived from `substr(md5(uuid), 0, 12)` (about 48 bits of entropy).
- Preview links never expire.

### Workarounds

If you cannot upgrade immediately:

- Restrict backend access so that only trusted users can reach the administration interface.
- Apply the fix manually by adding a VIEW permission check (via `SecurityCheckerInterface` and the resource's security context) inside `PreviewLinkManager::generate()` and `revoke()`.

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-65cv-w493-7vhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-82394
- https://github.com/sulu/sulu/commit/44d8844c3514a70b769ab791b9530df806240fab
- https://github.com/sulu/sulu
- https://github.com/sulu/sulu/releases/tag/2.6.25
- https://github.com/sulu/sulu/releases/tag/3.0.8
