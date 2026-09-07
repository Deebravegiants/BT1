# [C] Unsafe defaults in `remark-html`

## Summary
Severity: Critical
Advisory: GHSA-9q5w-79cv-947m
CVE: CVE-2021-39199
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-9q5w-79cv-947m
Type: github-advisory

## Affected
- npm: `remark-html` — affected >=0 <13.0.2
- npm: `remark-html` — affected >=14.0.0 <14.0.1

## Details
### Impact

The documentation of `remark-html` has mentioned that it was safe by default. In practise the default was never safe and had to be opted into. This means arbitrary HTML can be passed through leading to potential XSS attacks.

### Patches

The problem has been patched in 13.0.2 and 14.0.1: `remark-html` is now safe by default, and the implementation matches the documentation.

### Workarounds

On older affected versions, pass `sanitize: true`, like so:

```diff
-  .use(remarkHtml)
+  .use(remarkHtml, {sanitize: true})
```

### References

n/a

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [`remark-html`](https://github.com/remarkjs/remark-html)
* Email us at [security@unifiedjs.com](mailto:security@unifiedjs.com)

## References
- https://github.com/remarkjs/remark-html/security/advisories/GHSA-9q5w-79cv-947m
- https://nvd.nist.gov/vuln/detail/CVE-2021-39199
- https://github.com/remarkjs/remark-html/commit/b75c9dde582ad87ba498e369c033dc8a350478c1
- https://github.com/remarkjs/remark-html
- https://github.com/remarkjs/remark-html/releases/tag/14.0.1
- https://www.npmjs.com/package/remark-html
