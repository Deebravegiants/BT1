# [M] follow-redirects' Proxy-Authorization header kept across hosts

## Summary
Severity: Medium
Advisory: GHSA-cxjh-pqwp-8mfp
CVE: CVE-2024-28849
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-14
Source: https://github.com/advisories/GHSA-cxjh-pqwp-8mfp
Type: github-advisory

## Affected
- npm: `follow-redirects` — affected >=0 <1.15.6

## Details
When using [axios](https://github.com/axios/axios), its dependency follow-redirects only clears authorization header during cross-domain redirect, but allows the proxy-authentication header which contains credentials too.

## Steps To Reproduce & PoC

Test code:

```js
const axios = require('axios');

axios.get('http://127.0.0.1:10081/', {
 headers: {
 'AuThorization': 'Rear Test',
 'ProXy-AuthoriZation': 'Rear Test',
 'coOkie': 't=1'
 }
})
 .then((response) => {
 console.log(response);
 })
```

When I meet the cross-domain redirect, the sensitive headers like authorization and cookie are cleared, but proxy-authentication header is kept.

## Impact

This vulnerability may lead to credentials leak.

## Recommendations

Remove proxy-authentication header during cross-domain redirect

### Recommended Patch

[follow-redirects/index.js:464](https://github.com/follow-redirects/follow-redirects/commit/c4f847f85176991f95ab9c88af63b1294de8649b)

```diff
- removeMatchingHeaders(/^(?:authorization|cookie)$/i, this._options.headers);
+ removeMatchingHeaders(/^(?:authorization|proxy-authorization|cookie)$/i, this._options.headers);
```

## References
- https://github.com/follow-redirects/follow-redirects/security/advisories/GHSA-cxjh-pqwp-8mfp
- https://nvd.nist.gov/vuln/detail/CVE-2024-28849
- https://github.com/psf/requests/issues/1885
- https://github.com/follow-redirects/follow-redirects/commit/c4f847f85176991f95ab9c88af63b1294de8649b
- https://hackerone.com/reports/2390009
- https://fetch.spec.whatwg.org/#authentication-entries
- https://github.com/follow-redirects/follow-redirects
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VOIF4EPQUCKDBEVTGRQDZ3CGTYQHPO7Z
