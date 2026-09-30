# [M] Regular Expression Denial of Service in ssri

## Summary
Severity: Medium
Advisory: GHSA-325j-24f4-qv5x
CVE: CVE-2018-7651
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-03-07
Source: https://github.com/advisories/GHSA-325j-24f4-qv5x
Type: github-advisory

## Affected
- npm: `ssri` — affected >=0 <5.2.2

## Details
Version of `ssri` prior to 5.2.2 are vulnerable to regular expression denial of service (ReDoS) when using strict mode.


## Recommendation

Update to version 5.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7651
- https://github.com/zkat/ssri/issues/10
- https://github.com/zkat/ssri/commit/d0ebcdc22cb5c8f47f89716d08b3518b2485d65d
- https://github.com/advisories/GHSA-325j-24f4-qv5x
- https://github.com/zkat/ssri
- https://www.npmjs.com/advisories/565
