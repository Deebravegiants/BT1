# [M] Cross-Site Scripting in nunjucks

## Summary
Severity: Medium
Advisory: GHSA-f7ph-p5rv-phw2
CVE: CVE-2016-10547
CWE: CWE-79
Ecosystem: npm
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-f7ph-p5rv-phw2
Type: github-advisory

## Affected
- npm: `nunjucks` — affected >=0 <2.4.3

## Details
Affected versions of `nunjucks` do not properly escape specially structured user input in template vars when in auto-escape mode, resulting in a cross-site scripting vulnerability.

## Proof of Concept

By using an array for the keys in a template var, escaping is bypassed.
```javascript
name[]=<script>alert(1)</script>
```

A full PoC is available in the references section.


## Recommendation

Update to version 2.4.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10547
- https://github.com/mozilla/nunjucks/issues/835
- https://github.com/advisories/GHSA-f7ph-p5rv-phw2
- https://github.com/matt-/nunjucks_test
- https://www.npmjs.com/advisories/147
