# [M] SCEditor has DOM XSS via emoticon URL/HTML injection

## Summary
Severity: Medium
Advisory: GHSA-25fq-6qgg-qpj8
CVE: CVE-2026-25581
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-25fq-6qgg-qpj8
Type: github-advisory

## Affected
- npm: `sceditor` — affected >=0 <3.2.1

## Details
If an attacker has the ability control configuration options passed to `sceditor.create()`, like `emoticons`, `charset`, etc. then it's possible for them to trigger an XSS attack due to lack of sanitisation of configuration options.

Proof of concept:

```js
sceditor.create(textarea, {
  emoticons: {
    dropdown: { ':)': { url: 'x" onerror="window.__xss = true' } }
  }
});
```

## References
- https://github.com/samclarke/SCEditor/security/advisories/GHSA-25fq-6qgg-qpj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25581
- https://github.com/samclarke/SCEditor/commit/5733aed4f0e257cb78e1ba191715fc458cbd473d
- https://github.com/samclarke/SCEditor
