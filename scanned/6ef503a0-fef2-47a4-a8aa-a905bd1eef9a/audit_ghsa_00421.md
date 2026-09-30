# [M] Denial of Service in protobufjs

## Summary
Severity: Medium
Advisory: GHSA-762f-c2wg-m8c8
CVE: CVE-2018-3738
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-762f-c2wg-m8c8
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=6.0.0 <6.8.6
- npm: `protobufjs` — affected >=0 <5.0.3

## Details
Versions of `protobufjs` before 5.0.3 and 6.8.6 are vulnerable to a regular expression denial of service when parsing crafted invalid *.proto files.


## Recommendation

Update to version 5.0.3, 6.8.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3738
- https://hackerone.com/reports/319576
- https://github.com/advisories/GHSA-762f-c2wg-m8c8
- https://github.com/dcodeIO/protobuf.js/blob/6.8.5/src/parse.js#L27
- https://www.npmjs.com/advisories/605
