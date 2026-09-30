# [H] The AuthKit Remix Library renders sensitive auth data in HTML

## Summary
Severity: High
Advisory: GHSA-v3gr-w9gf-23cx
CVE: CVE-2025-55009
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-v3gr-w9gf-23cx
Type: github-advisory

## Affected
- npm: `@workos-inc/authkit-remix` — affected >=0 <0.15.0

## Details
### Summary

Before `0.15.0`, `@workos-inc/authkit-remix` returned sensitive authentication artifacts from the `authkitLoader`, specifically `sealedSession` and `accessToken`. Because these values were returned from the loader, they were embedded into the server-rendered HTML and became readable by any script with access to the page’s DOM (e.g., in the presence of XSS or a malicious browser extension).

*   **Impact:** Exposure of these secrets can lead to session hijacking and unauthorized API access.
*   **Fix:** Version `0.15.0` changes the default behavior so the loader no longer returns `sealedSession`/`accessToken`. A secure server-side mechanism is provided to fetch an access token when needed.

### Patches

Patched in [v0.15.0](https://github.com/workos/authkit-remix/releases/tag/v0.15.0).

## References
- https://github.com/workos/authkit-remix/security/advisories/GHSA-v3gr-w9gf-23cx
- https://nvd.nist.gov/vuln/detail/CVE-2025-55009
- https://github.com/workos/authkit-remix/commit/20102afc74bf3dd5150a975a098067fb406b90b6
- https://github.com/workos/authkit-remix
- https://github.com/workos/authkit-remix/releases/tag/v0.15.0
- https://osv.dev/vulnerability/CVE-2025-55009
- https://osv.dev/vulnerability/GHSA-v3gr-w9gf-23cx
