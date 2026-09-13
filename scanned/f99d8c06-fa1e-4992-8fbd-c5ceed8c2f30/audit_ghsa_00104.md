# [M] superagent vulnerable to zip bomb attacks

## Summary
Severity: Medium
Advisory: GHSA-8225-6cvr-8pqp
CVE: CVE-2017-16129
CWE: CWE-400, CWE-409
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-08-09
Source: https://github.com/advisories/GHSA-8225-6cvr-8pqp
Type: github-advisory

## Affected
- npm: `superagent` — affected >=0 <3.7.0

## Details
Affected versions of `superagent` do not check the post-decompression size of ZIP compressed HTTP responses prior to decompressing. This results in the package being vulnerable to a [ZIP bomb](https://en.wikipedia.org/wiki/Zip_bomb) attack, where an extremely small ZIP file becomes many orders of magnitude larger when decompressed. 

This may result in unrestrained CPU/Memory/Disk consumption, causing a denial of service condition.


## Recommendation

Update to version 3.7.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16129
- https://github.com/visionmedia/superagent/issues/1259
- https://en.wikipedia.org/wiki/Zip_bomb
- https://github.com/advisories/GHSA-8225-6cvr-8pqp
- https://www.npmjs.com/advisories/479
