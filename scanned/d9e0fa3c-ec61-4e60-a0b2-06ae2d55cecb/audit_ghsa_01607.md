# [M] Prototype Pollution in highlight.js

## Summary
Severity: Medium
Advisory: GHSA-vfrc-7r7c-w9mx
CVE: CVE-2020-26237
CWE: CWE-471
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-11-24
Source: https://github.com/advisories/GHSA-vfrc-7r7c-w9mx
Type: github-advisory

## Affected
- npm: `highlight.js` — affected >=0 <9.18.2
- npm: `highlight.js` — affected >=10.0.0 <10.1.2

## Details
### Impact

Affected versions of this package are vulnerable to Prototype Pollution.  A malicious HTML code block can be crafted that will result in prototype pollution of the base object's prototype during highlighting.  If you allow users to insert custom HTML code blocks into your page/app via parsing Markdown code blocks (or similar) and do not filter the language names the user can provide you may be vulnerable. 

The pollution should just be harmless data but this can cause problems for applications not expecting these properties to exist and can result in strange behavior or application crashes, i.e. a potential DOS vector. 

_If your website or application does not render user provided data it should be unaffected._

### Patches

Versions 9.18.2 and 10.1.2 and newer include fixes for this vulnerability.  If you are using version 7 or 8 you are encouraged to upgrade to a newer release.

### Workarounds

#### Patch your library

Manually patch your library to create null objects for both `languages` and `aliases`:

```js
const HLJS = function(hljs) {
  // ...
  var languages = Object.create(null);
  var aliases = Object.create(null);
```

#### Filter out bad data from end users:

Filter the language names that users are allowed to inject into your HTML to guarantee they are valid.

### References

* [What is Prototype Pollution?](https://codeburst.io/what-is-prototype-pollution-49482fc4b638)
* https://github.com/highlightjs/highlight.js/pull/2636

### For more information

If you have any questions or comments about this advisory:

* Please file an issue against [highlight.js](https://github.com/highlightjs/highlight.js/issues/)

## References
- https://github.com/highlightjs/highlight.js/security/advisories/GHSA-vfrc-7r7c-w9mx
- https://nvd.nist.gov/vuln/detail/CVE-2020-26237
- https://github.com/highlightjs/highlight.js/pull/2636
- https://github.com/highlightjs/highlight.js/commit/7241013ae011a585983e176ddc0489a7a52f6bb0
- https://github.com/highlightjs/highlight.js
- https://lists.debian.org/debian-lts-announce/2020/12/msg00041.html
- https://www.npmjs.com/package/highlight.js
- https://www.oracle.com/security-alerts/cpujul2022.html
