# [M] Cross-site Scripting in quill

## Summary
Severity: Medium
Advisory: GHSA-4943-9vgg-gr5r
CVE: CVE-2021-3163
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-4943-9vgg-gr5r
Type: github-advisory

## Affected
- npm: `quill` — affected >=0

## Details
A vulnerability in the HTML editor of Slab Quill allows an attacker to execute arbitrary JavaScript by storing an XSS payload (a crafted `onloadstart` attribute of an IMG element) in a text field. No patch exists and no further releases are planned.

This CVE is disputed. Researchers have claimed that this issue is not within the product itself, but is intended behavior in a web browser. More information can be found [here](https://github.com/quilljs/quill/issues/3364).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3163
- https://github.com/quilljs/quill/issues/3273
- https://github.com/quilljs/quill/issues/3359
- https://github.com/quilljs/quill/issues/3364
- https://burninatorsec.blogspot.com/2021/04/cve-2021-3163-xss-slab-quill-js.html
- https://github.com/quilljs/quill
- https://quilljs.com
