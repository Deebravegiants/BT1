# [M] Babel has inefficient RegExp complexity in generated code with .replace when transpiling named capturing groups

## Summary
Severity: Medium
Advisory: GHSA-968p-4wvh-cqc8
CVE: CVE-2025-27789
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-968p-4wvh-cqc8
Type: github-advisory

## Affected
- npm: `@babel/helpers` — affected >=0 <7.26.10
- npm: `@babel/runtime` — affected >=0 <7.26.10
- npm: `@babel/runtime-corejs2` — affected >=0 <7.26.10
- npm: `@babel/runtime-corejs3` — affected >=0 <7.26.10
- npm: `@babel/helpers` — affected >=8.0.0-alpha.0 <8.0.0-alpha.17
- npm: `@babel/runtime` — affected >=8.0.0-alpha.0 <8.0.0-alpha.17
- npm: `@babel/runtime-corejs2` — affected >=8.0.0-alpha.0 <8.0.0-alpha.17
- npm: `@babel/runtime-corejs3` — affected >=8.0.0-alpha.0 <8.0.0-alpha.17

## Details
### Impact

When using Babel to compile [regular expression named capturing groups](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Regular_expressions/Named_capturing_group), Babel will generate a polyfill for the `.replace` method that has quadratic complexity on some specific replacement pattern strings (i.e. the second argument passed to `.replace`).

Your generated code is vulnerable if _all_ the following conditions are true:
- You use Babel to compile [regular expression named capturing groups](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Regular_expressions/Named_capturing_group)
- You use the `.replace` method on a regular expression that contains named capturing groups
- **Your code uses untrusted strings as the second argument of `.replace`**

If you are using `@babel/preset-env` with the [`targets`](https://babeljs.io/docs/options#targets) option, the transform that injects the vulnerable code is automatically enabled if:
- you use [_duplicated_ named capturing groups](https://github.com/tc39/proposal-duplicate-named-capturing-groups), and target any browser older than Chrome/Edge 126, Opera 112, Firefox 129, Safari 17.4, or Node.js 23
- you use any [named capturing groups](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Regular_expressions/Named_capturing_group), and target any browser older than Chrome 64, Opera 71, Edge 79, Firefox 78, Safari 11.1, or Node.js 10

You can verify what transforms `@babel/preset-env` is using by enabling the [`debug` option](https://babeljs.io/docs/babel-preset-env#debug).


### Patches

This problem has been fixed in `@babel/helpers` and `@babel/runtime` 7.26.10 and 8.0.0-alpha.17, please upgrade. It's likely that you do not directly depend on `@babel/helpers`, and instead you depend on `@babel/core` (which itself depends on `@babel/helpers`). Upgrading to `@babel/core` 7.26.10 is not required, but it guarantees that you are on a new enough `@babel/helpers` version.

Please note that just updating your Babel dependencies is not enough: you will also need to re-compile your code.

### Workarounds

If you are passing user-provided strings as the second argument of `.replace` on regular expressions that contain named capturing groups, validate the input and make sure it does not contain the substring `$<` if it's then not followed by `>` (possibly with other characters in between).

### References

This vulnerability was reported and fixed in https://github.com/babel/babel/pull/17173.

## References
- https://github.com/babel/babel/security/advisories/GHSA-968p-4wvh-cqc8
- https://nvd.nist.gov/vuln/detail/CVE-2025-27789
- https://github.com/babel/babel/pull/17173
- https://github.com/babel/babel/commit/d5952e80c0faa5ec20e35085531b6e572d31dad4
- https://github.com/babel/babel
