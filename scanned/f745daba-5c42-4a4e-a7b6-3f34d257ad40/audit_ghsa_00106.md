# [H] Regular Expression Denial of Service in timespan

## Summary
Severity: High
Advisory: GHSA-f523-2f5j-gfcg
CVE: CVE-2017-16115
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-08-29
Source: https://github.com/advisories/GHSA-f523-2f5j-gfcg
Type: github-advisory

## Affected
- npm: `timespan` — affected >=0

## Details
Affected versions of `timespan` are vulnerable to a regular expression denial of service when parsing dates.

The amplification for this vulnerability is significant, with 50,000 characters resulting in the event loop being blocked for around 10 seconds.


## Recommendation

No direct patch is available for this vulnerability.

Currently, the best available solution is to use a functionally equivalent alternative package.

It is also sufficient to ensure that user input is not being passed into `timespan`, or that the maximum length of such user input is drastically reduced. Limiting the input length to 150 characters should be sufficient in most cases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16115
- https://github.com/indexzero/TimeSpan.js/issues/10
- https://github.com/advisories/GHSA-f523-2f5j-gfcg
- https://www.npmjs.com/advisories/533
