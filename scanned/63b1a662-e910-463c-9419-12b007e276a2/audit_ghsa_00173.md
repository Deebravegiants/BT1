# [H] method-override ReDoS when untrusted user input passed into X-HTTP-Method-Override header

## Summary
Severity: High
Advisory: GHSA-qx2f-477c-35rq
CVE: CVE-2017-16136
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-qx2f-477c-35rq
Type: github-advisory

## Affected
- npm: `method-override` — affected >=1.0.2 <2.3.10
- npm: `method-override` — affected >=2.0.0 <2.3.10

## Details
Affected versions of `method-override` are vulnerable to a regular expression denial of service vulnerability when untrusted user input is passed into the `X-HTTP-Method-Override` header.


## Recommendation

Update to version 2.3.10 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16136
- https://github.com/expressjs/method-override/commit/4c58835a61fdf7a8e070d6f8ecd5379a961d0987
- https://github.com/expressjs/method-override
- https://www.npmjs.com/advisories/538
