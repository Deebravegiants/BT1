# [M] Macro in MathJax running untrusted Javascript within a web browser

## Summary
Severity: Medium
Advisory: GHSA-3c48-6pcv-88rm
CVE: CVE-2018-1999024
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-27
Source: https://github.com/advisories/GHSA-3c48-6pcv-88rm
Type: github-advisory

## Affected
- npm: `mathjax` — affected >=0 <2.7.4

## Details
MathJax version prior to version 2.7.4 contains a Cross Site Scripting (XSS) vulnerability in the `\unicode{}` macro that can result in Potentially untrusted Javascript running within a web browser. This attack appear to be exploitable via The victim must view a page where untrusted content is processed using Mathjax. This vulnerability appears to have been fixed in 2.7.4 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999024
- https://github.com/mathjax/MathJax/commit/a55da396c18cafb767a26aa9ad96f6f4199852f1
- https://blog.bentkowski.info/2018/06/xss-in-google-colaboratory-csp-bypass.html
- https://github.com/advisories/GHSA-3c48-6pcv-88rm
- https://github.com/mathjax/MathJax
