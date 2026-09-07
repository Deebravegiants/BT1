# [M] mdast-util-to-hast has unsanitized class attribute

## Summary
Severity: Medium
Advisory: GHSA-4fh9-h7wg-q85m
CVE: CVE-2025-66400
CWE: CWE-20, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-4fh9-h7wg-q85m
Type: github-advisory

## Affected
- npm: `mdast-util-to-hast` — affected >=13.0.0 <13.2.1

## Details
### Impact

Multiple (unprefixed) classnames could be added in markdown source by using character references.
This could make rendered user supplied markdown `code` elements appear like the rest of the page.
The following markdown:

````markdown
```js&#x20;xss
```
````

Would create `<pre><code class="language-js xss"></code></pre>`
If your page then applied `.xss` classes (or listeners in JS), those apply to this element.
For more info see <https://github.com/ChALkeR/notes/blob/master/Improper-markup-sanitization.md#unsanitized-class-attribute>

### Patches

The bug was patched. When using regular semver, run `npm install`. For exact ranges, make sure to use `13.2.1`.

### Workarounds

Update.

### References

* bug introduced in https://github.com/syntax-tree/mdast-util-to-hast/commit/6fc783ae6abdeb798fd5a68e7f3f21411dde7403
* bug fixed in https://github.com/syntax-tree/mdast-util-to-hast/commit/ab3a79570a1afbfa7efef5d4a0cd9b5caafbc5d7

## References
- https://github.com/syntax-tree/mdast-util-to-hast/security/advisories/GHSA-4fh9-h7wg-q85m
- https://nvd.nist.gov/vuln/detail/CVE-2025-66400
- https://github.com/syntax-tree/mdast-util-to-hast/commit/6fc783ae6abdeb798fd5a68e7f3f21411dde7403
- https://github.com/syntax-tree/mdast-util-to-hast/commit/ab3a79570a1afbfa7efef5d4a0cd9b5caafbc5d7
- https://github.com/syntax-tree/mdast-util-to-hast
