# [H] Regular Expression Denial of Service in djvalidator

## Summary
Severity: High
Advisory: GHSA-v6wh-2wvh-c8x5
CVE: CVE-2020-7779
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-v6wh-2wvh-c8x5
Type: github-advisory

## Affected
- npm: `djvalidator` — affected >=0

## Details
All versions of package djvalidator are vulnerable to Regular Expression Denial of Service (ReDoS) by sending crafted invalid emails - for example, 
`--@------------------------------------------------------------------------------------------------------------------------!`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7779
- https://snyk.io/vuln/SNYK-JS-DJVALIDATOR-1018709
