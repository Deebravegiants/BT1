# [M] nuxt vulnerable to Cross-site Scripting in navigateTo if used after SSR

## Summary
Severity: Medium
Advisory: GHSA-vf6r-87q4-2vjf
CVE: CVE-2024-34343
CWE: CWE-79, CWE-83
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-vf6r-87q4-2vjf
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=0 <3.12.4

## Details
### Summary
The `navigateTo` function attempts to blockthe `javascript:` protocol, but does not correctly use API's provided by `unjs/ufo`. This library also contains parsing discrepancies.

### Details
The function first tests to see if the specified [URL has a protocol](https://github.com/nuxt/nuxt/blob/fa9d43753d25fc2e8c3107f194b2bab6d4ebcb9a/packages/nuxt/src/app/composables/router.ts#L142). This uses the [unjs/ufo](https://github.com/unjs/ufo) package for URL parsing. This function works effectively, and returns true for a `javascript:` protocol.

After this, the URL is parsed using the [`parseURL`](https://github.com/unjs/ufo/blob/e970686b2acae972136f478732450f6a2f1ab5e5/src/parse.ts#L47) function. This function will refuse to parse poorly formatted URLs. Parsing `javascript:alert(1)` returns null/"" for all values. 

Next, the protocol of the URL is then checked using the [`isScriptProtocol`](https://github.com/unjs/ufo/blob/e970686b2acae972136f478732450f6a2f1ab5e5/src/utils.ts#L74) function. This function simply checks the input against a list of protocols, and does not perform any parsing. 

The combination of refusing to parse poorly formatted URLs, and not performing additional parsing means that script checks fail as no protocol can be found. Even if a protocol was identified, whitespace is not stripped in the `parseURL` implementation, bypassing the `isScriptProtocol` checks. 

Certain special protocols are identified at the top of [`parseURL`](https://github.com/unjs/ufo/blob/e970686b2acae972136f478732450f6a2f1ab5e5/src/parse.ts#L49). Inserting a newline or tab into this sequence will block the special protocol check, and bypass the latter checks. 

### PoC
POC - https://stackblitz.com/edit/nuxt-xss-navigateto?file=app.vue

Attempt payload X, then attempt payload Y.

### Impact
XSS, access to cookies, make requests on user's behalf. 

### Recommendations
As always with these bugs, the `URL` constructor provided by the browser is always the safest method of parsing a URL. 

Given the cross-platform requirements of nuxt/ufo a more appropriate solution is to make parsing consistent between functions, and to adapt parsing to be more consistent with the [WHATWG URL specification](https://url.spec.whatwg.org/).

### Note
I've reported this vulnerability here as it is unclear if this is a bug in ufo or a misuse of the ufo library.

This ONLY has impact after SSR has occurred, the `javascript:` protocol within a location header does not trigger XSS.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-vf6r-87q4-2vjf
- https://nvd.nist.gov/vuln/detail/CVE-2024-34343
- https://github.com/nuxt/nuxt
