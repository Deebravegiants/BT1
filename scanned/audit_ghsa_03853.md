# [H] Regular Expression Denial of Service in csv-parse

## Summary
Severity: High
Advisory: GHSA-582f-p4pg-xc74
CVE: CVE-2019-17592
CWE: CWE-20, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-10-15
Source: https://github.com/advisories/GHSA-582f-p4pg-xc74
Type: github-advisory

## Affected
- npm: `csv-parse` — affected >=0 <4.4.6

## Details
Versions of `csv-parse` prior to 4.4.6 are vulnerable to Regular Expression Denial of Service. The `__isInt()` function contains a malformed regular expression that processes large specially-crafted input very slowly, leading to a Denial of Service. This is triggered when using the `cast` option.


## Recommendation

Upgrade to version 4.4.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17592
- https://github.com/adaltas/node-csv-parse/commit/b9d35940c6815cdf1dfd6b21857a1f6d0fd51e4a
- https://github.com/adaltas/node-csv-parse
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z36UKPO5F3PQ3Q2POMF5LEKXWAH5RUFP
- https://security.netapp.com/advisory/ntap-20191127-0002
- https://www.npmjs.com/advisories/1171
