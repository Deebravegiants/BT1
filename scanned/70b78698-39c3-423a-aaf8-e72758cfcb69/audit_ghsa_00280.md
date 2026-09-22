# [H] Regular Expression Denial of Service in marked

## Summary
Severity: High
Advisory: GHSA-x5pg-88wf-qq4p
CVE: CVE-2017-16114
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-x5pg-88wf-qq4p
Type: github-advisory

## Affected
- npm: `marked` — affected >=0 <0.3.9

## Details
Affected versions of `marked` are vulnerable to a regular expression denial of service. 

The amplification in this vulnerability is significant, with 1,000 characters resulting in the event loop being blocked for around 6 seconds.


## Recommendation

Update to version 0.3.9 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16114
- https://github.com/chjj/marked/issues/937
- https://github.com/advisories/GHSA-x5pg-88wf-qq4p
- https://www.npmjs.com/advisories/531
