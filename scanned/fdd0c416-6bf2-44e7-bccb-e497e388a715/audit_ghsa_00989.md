# [C] Unsafe eval() in summit allows arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-cwcp-6c48-fm7m
CVE: CVE-2017-16020
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-cwcp-6c48-fm7m
Type: github-advisory

## Affected
- npm: `summit` — affected >=0.1.0

## Details
Affected versions of `summit` allow attackers to execute arbitrary commands via collection names when using the `PouchDB` driver.

## Recommendation

No direct patch is available at this time.

Currently, the best option to mitigate the issue is to avoid using the `PouchDB` driver, as the package author has abandoned this feature entirely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16020
- https://github.com/notduncansmith/summit/issues/23
- https://github.com/fredhohman/summit
