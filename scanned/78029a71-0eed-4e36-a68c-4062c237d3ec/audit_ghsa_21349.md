# [H] kangax html-minifier REDoS vulnerability

## Summary
Severity: High
Advisory: GHSA-pfq8-rq6v-vf5m
CVE: CVE-2022-37620
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-31
Source: https://github.com/advisories/GHSA-pfq8-rq6v-vf5m
Type: github-advisory

## Affected
- npm: `html-minifier` — affected >=0

## Details
A Regular Expression Denial of Service (ReDoS) flaw was found in kangax html-minifier 4.0.0 because of the reCustomIgnore regular expression.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37620
- https://github.com/kangax/html-minifier/issues/1135
- https://github.com/kangax/html-minifier
- https://github.com/kangax/html-minifier/blob/51ce10f4daedb1de483ffbcccecc41be1c873da2/src/htmlminifier.js#L1338
- https://github.com/kangax/html-minifier/blob/51ce10f4daedb1de483ffbcccecc41be1c873da2/src/htmlminifier.js#L294
- https://security.snyk.io/vuln/SNYK-JS-HTMLMINIFIER-3091181
