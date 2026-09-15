# [M] @workos/authkit-session has an Open Redirect via state-derived redirect target

## Summary
Severity: Medium
Advisory: GHSA-vvvv-983w-r7pv
CVE: CVE-2026-42565
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-vvvv-983w-r7pv
Type: github-advisory

## Affected
- npm: `@workos/authkit-session` — affected >=0 <0.5.1

## Details
An open redirect vulnerability exists in `AuthService.handleCallback` due to insufficient validation of the `returnPathname` value derived from the OAuth `state` parameter.

The `state` parameter is round-tripped through the identity provider (IdP) and can be influenced by an attacker. The handleCallback function decodes and returns returnPathname without enforcing restrictions on origin or scheme. As a result, attacker-controlled values (e.g., `https://evil.com/`, `//evil.com`, or similar variants) may be returned to the application.

If this value is used directly in a redirect (e.g., via an HTTP `Location` header, framework redirect helpers, or client-side navigation), it may cause the user to be redirected to an external, attacker-controlled site.

**Security Impact**
This issue may be used to facilitate phishing or user redirection attacks by leveraging the trust of the originating domain. For example, an attacker could craft a link that directs a user through a legitimate authentication flow and then redirects them to an external site.

The severity depends on how `returnPathname` is used by the application. Exploitation requires:

* The application to use `returnPathname` as a redirect target, and
* The absence of downstream validation or allowlisting

This vulnerability does not enable authentication bypass, token disclosure, or direct account compromise on its own, but may increase the effectiveness of social engineering attacks when combined with user interaction.

**Vulnerability Type**
CWE-601: URL Redirection to Untrusted Site (Open Redirect)

**Patches**
Patched in https://github.com/workos/authkit-session/releases/tag/v0.5.1

## References
- https://github.com/workos/authkit-session/security/advisories/GHSA-vvvv-983w-r7pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-42565
- https://github.com/workos/authkit-session/commit/f56e1d6214a93160759e5677b7a3d772b244db39
- https://github.com/workos/authkit-session
- https://github.com/workos/authkit-session/releases/tag/v0.5.1
