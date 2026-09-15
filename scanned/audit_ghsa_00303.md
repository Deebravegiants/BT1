# [H] Path Traversal in localhost-now

## Summary
Severity: High
Advisory: GHSA-2gjg-5x33-mmp2
CVE: CVE-2018-3729
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-25
Source: https://github.com/advisories/GHSA-2gjg-5x33-mmp2
Type: github-advisory

## Affected
- npm: `localhost-now` — affected >=0 <1.0.2

## Details
Versions of `localhost-now` before 1.0.2 are vulnerable to path traversal. This allows a remote attacker to read the content of an arbitrary file.


## Recommendation

Update to version 1.0.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3729
- https://github.com/DCKT/localhost-now/commit/30b004c7f145d677df8800a106c2edc982313995#diff-b9cfc7f2cdf78a7f4b91a753d10865a2
- https://hackerone.com/reports/312889
- https://github.com/advisories/GHSA-2gjg-5x33-mmp2
- https://www.npmjs.com/advisories/582
