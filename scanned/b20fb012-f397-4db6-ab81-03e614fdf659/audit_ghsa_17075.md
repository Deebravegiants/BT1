# [M] Express.js Open Redirect in malformed URLs

## Summary
Severity: Medium
Advisory: GHSA-rv95-896h-c2vc
CVE: CVE-2024-29041
CWE: CWE-1286, CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-rv95-896h-c2vc
Type: github-advisory

## Affected
- npm: `express` — affected >=0 <4.19.2
- npm: `express` — affected >=5.0.0-alpha.1 <5.0.0-beta.3

## Details
### Impact

Versions of Express.js prior to 4.19.2 and pre-release alpha and beta versions before 5.0.0-beta.3 are affected by an open redirect vulnerability using malformed URLs.

When a user of Express performs a redirect using a user-provided URL Express performs an encode [using `encodeurl`](https://github.com/pillarjs/encodeurl) on the contents before passing it to the `location` header. This can cause malformed URLs to be evaluated in unexpected ways by common redirect allow list implementations in Express applications, leading to an Open Redirect via bypass of a properly implemented allow list.

The main method impacted is `res.location()` but this is also called from within `res.redirect()`.

### Patches

https://github.com/expressjs/express/commit/0867302ddbde0e9463d0564fea5861feb708c2dd
https://github.com/expressjs/express/commit/0b746953c4bd8e377123527db11f9cd866e39f94

An initial fix went out with `express@4.19.0`, we then patched a feature regression in `4.19.1` and added improved handling for the bypass in `4.19.2`.

### Workarounds

The fix for this involves pre-parsing the url string with either `require('node:url').parse` or `new URL`. These are steps you can take on your own before passing the user input string to `res.location` or `res.redirect`.

### Resources

https://github.com/expressjs/express/pull/5539
https://github.com/koajs/koa/issues/1800
https://expressjs.com/en/4x/api.html#res.location

## References
- https://github.com/expressjs/express/security/advisories/GHSA-rv95-896h-c2vc
- https://nvd.nist.gov/vuln/detail/CVE-2024-29041
- https://github.com/koajs/koa/issues/1800
- https://github.com/expressjs/express/pull/5539
- https://github.com/expressjs/express/commit/0867302ddbde0e9463d0564fea5861feb708c2dd
- https://github.com/expressjs/express/commit/0b746953c4bd8e377123527db11f9cd866e39f94
- https://expressjs.com/en/4x/api.html#res.location
- https://github.com/expressjs/express
