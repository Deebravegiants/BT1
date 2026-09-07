# [H] The AuthKit React Router Library rendered sensitive auth data in HTML

## Summary
Severity: High
Advisory: GHSA-vqvc-9q8x-vmq6
CVE: CVE-2025-55008
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-vqvc-9q8x-vmq6
Type: github-advisory

## Affected
- npm: `@workos-inc/authkit-react-router` — affected >=0 <0.7.0

## Details
In versions before `0.7.0`, `@workos-inc/authkit-react-router` exposed sensitive authentication artifacts — specifically `sealedSession` and `accessToken` by returning them from the `authkitLoader`. This caused them to be rendered into the browser HTML.

### Impact
This information disclosure could lead to session hijacking in environments where cross-site scripting (XSS), malicious browser extensions, or local inspection is possible.
 
### Patches
Patched in [https://github.com/workos/authkit-react-router/releases/tag/v0.7.0](https://github.com/workos/authkit-react-router/releases/tag/v0.7.0)

In patched versions:
- `sealedSession` and `accessToken` are no longer returned by default from the `authkitLoader`.
- A secure server-side mechanism is provided to fetch an access token as needed.

## References
- https://github.com/workos/authkit-react-router/security/advisories/GHSA-vqvc-9q8x-vmq6
- https://nvd.nist.gov/vuln/detail/CVE-2025-55008
- https://github.com/workos/authkit-react-router/commit/607caac658784962bab76e227f9c5820d0b9a9e5
- https://github.com/workos/authkit-react-router
- https://github.com/workos/authkit-react-router/releases/tag/v0.7.0
