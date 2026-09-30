# [H] PhantomJS Arbitrary File Read

## Summary
Severity: High
Advisory: GHSA-x43g-gj9x-838x
CVE: CVE-2019-17221
CWE: CWE-552
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x43g-gj9x-838x
Type: github-advisory

## Affected
- npm: `phantomjs` — affected >=0

## Details
PhantomJS through 2.1.1 has an arbitrary file read vulnerability, as demonstrated by an XMLHttpRequest for a `file://` URI. The vulnerability exists in the `page.open()` function of the webpage module, which loads a specified URL and calls a given callback. An attacker can supply a specially crafted HTML file, as user input, that allows reading arbitrary files on the filesystem. For example, if `page.render()` is the function callback, this generates a PDF or an image of the targeted file. **NOTE**: this product is no longer developed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17221
- https://github.com/Medium/phantomjs
- https://web.archive.org/web/20191220171022/https://www.darkmatter.ae/blogs/breaching-the-perimeter-phantomjs-arbitrary-file-read
