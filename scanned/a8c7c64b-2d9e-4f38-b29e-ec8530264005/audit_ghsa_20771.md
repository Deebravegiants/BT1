# [M] @netlify/ipx vulnerable to Full Response SSRF and Stored XSS via Cache Poisoning and Improper Host Validation

## Summary
Severity: Medium
Advisory: GHSA-9jjv-524m-jm98
CVE: CVE-2022-39239
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-9jjv-524m-jm98
Type: github-advisory

## Affected
- npm: `@netlify/ipx` — affected >=0 <1.2.3

## Details
### Impact

By sending specially crafted headers an attacker can bypass the source image domain allowlist, causing the handler to load and return arbitrary images. Because the response is cached globally, this image will then be served to visitors without requiring those headers to be set. XSS can be achieved by requesting a malicious SVG with embedded scripts, which would then be served from the site domain. Note that this does not apply to images loaded in `<img>` tags, as scripts do not execute in this context. The image URL can be set in the header independently of the request URL, meaning any site images that have not previously been cached can have their cache poisoned.

### Patches
This problem has been fixed in version 1.2.3

### Workarounds

The problem is no longer exploitable on Netlify as the CDN now sanitizes the relevant header. Cached content can be cleared by re-deploying the site.

## References
- https://github.com/netlify/netlify-ipx/security/advisories/GHSA-9jjv-524m-jm98
- https://nvd.nist.gov/vuln/detail/CVE-2022-39239
- https://github.com/netlify/netlify-ipx/pull/61
- https://github.com/netlify/netlify-ipx/commit/dfa7505a8d47a76fd527570dc40737a61500759b
- https://github.com/netlify/netlify-ipx
- https://github.com/netlify/netlify-ipx/releases/tag/v1.2.3
