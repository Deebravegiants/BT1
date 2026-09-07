# [H] muhammara and hummus vulnerable to null pointer dereference on bad response object

## Summary
Severity: High
Advisory: GHSA-frp9-2v6r-gj97
CVE: CVE-2022-25885
CWE: CWE-690
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-frp9-2v6r-gj97
Type: github-advisory

## Affected
- npm: `hummus` — affected >=1.0.0 <1.0.111
- npm: `muhammara` — affected >=0 <2.6.0

## Details
The package muhammara before 2.6.0 and the package hummus before 1.0.111 are vulnerable to Denial of Service (DoS) when PDFStreamForResponse() is used with invalid data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25885
- https://github.com/galkahana/HummusJS/issues/439
- https://github.com/julianhille/MuhammaraJS/issues/188
- https://github.com/galkahana/HummusJS/commit/a9bf2520ab5abb69f9328906e406fbebfb36159a
- https://github.com/julianhille/MuhammaraJS/commit/0a6427eec82ef2978995e453de2dc0d6224dd46c
- https://github.com/julianhille/MuhammaraJS
- https://security.snyk.io/vuln/SNYK-JS-HUMMUS-3091139
- https://security.snyk.io/vuln/SNYK-JS-MUHAMMARA-3091137
