# [M] Leading white space bypasses protocol validation

## Summary
Severity: Medium
Advisory: GHSA-gmv4-r438-p67f
CVE: CVE-2022-24723
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-03
Source: https://github.com/advisories/GHSA-gmv4-r438-p67f
Type: github-advisory

## Affected
- npm: `urijs` — affected >=0 <1.19.9

## Details
### Impact
Whitespace characters are not removed from the beginning of the protocol, so URLs are not parsed properly and protocol validation mechanisms may fail.

### Patches
Patched in 1.19.9

### Workarounds
Remove leading whitespace from values before passing them to URI.parse (e.g. via `.href(value)` or `new URI(value)`), e.g. by using

```js
function remove_whitespace(url){
     const whitespace = /^[\x00-\x20\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff]+/;
     url = url.replace(whitespace, '')
     return url
}
```

### References
* https://huntr.dev/bounties/82ef23b8-7025-49c9-b5fc-1bb9885788e5/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [medialize/URI.js](https://github.com/medialize/URI.js/)

## References
- https://github.com/medialize/URI.js/security/advisories/GHSA-gmv4-r438-p67f
- https://nvd.nist.gov/vuln/detail/CVE-2022-24723
- https://github.com/medialize/URI.js/commit/86d10523a6f6e8dc4300d99d671335ee362ad316
- https://github.com/medialize/URI.js
- https://github.com/medialize/URI.js/releases/tag/v1.19.9
- https://huntr.dev/bounties/82ef23b8-7025-49c9-b5fc-1bb9885788e5
