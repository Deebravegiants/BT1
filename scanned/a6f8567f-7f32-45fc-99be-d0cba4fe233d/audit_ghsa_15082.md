# [M] CubeFS leaks users key in logs

## Summary
Severity: Medium
Advisory: GHSA-vwch-g97w-hfg2
CVE: CVE-2023-46742
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-vwch-g97w-hfg2
Type: github-advisory

## Affected
- Go: `github.com/cubefs/cubefs` — affected >=0 <3.3.1

## Details
CubeFS was found to leak users secret keys and access keys in the logs in multiple components.  When CubeCS creates new users, it leaks the users secret key. This could allow a lower-privileged user with access to the logs to retrieve sensitive information and impersonate other users with higher privileges than themselves. 

There is no evidence of this vulnerability being exploited in the wild. It was found during an ongoing security audit carried out by [Ada Logics](https://adalogics.com/) in collaboration with [OSTIF](https://ostif.org/) and the [CNCF](https://www.cncf.io/).

The issue has been patched in v3.3.1. There is no other mitigation than upgrading CubeFS.

## References
- https://github.com/cubefs/cubefs/security/advisories/GHSA-vwch-g97w-hfg2
- https://nvd.nist.gov/vuln/detail/CVE-2023-46742
- https://github.com/cubefs/cubefs/commit/8dccce6ac8dff3db44d7e9074094c7303a5ff5dd
- https://github.com/cubefs/cubefs
