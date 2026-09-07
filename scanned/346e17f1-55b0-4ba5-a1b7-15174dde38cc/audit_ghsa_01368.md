# [H] Cross-Site Scripting in nextcloud-vue-collections

## Summary
Severity: High
Advisory: GHSA-whv6-rj84-2vh2
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-whv6-rj84-2vh2
Type: github-advisory

## Affected
- npm: `nextcloud-vue-collections` — affected >=0 <0.4.2

## Details
Versions of `nextcloud-vue-collections` prior to 0.4.2 are vulnerable to Cross-Site Scripting (XSS).  The `v-tooltip` component has an insecure `defaultHTML` configuration that allows arbitrary JavaScript to be injected in the tooltip of a collection item. This allows attackers to execute arbitrary code in a victim's browser.


## Recommendation

Upgrade to version 0.4.2 or later.

## References
- https://github.com/juliushaertl/nextcloud-vue-collections/commit/8ec1fca214f003538cec4137792ede928f25f583
- https://github.com/juliushaertl/nextcloud-vue-collections
- https://www.npmjs.com/advisories/1442
