# [M] Cross-site Scripting Vulnerability in Statement Browser

## Summary
Severity: Medium
Advisory: GHSA-7rw2-3hhp-rc46
CVE: CVE-2024-26140
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-7rw2-3hhp-rc46
Type: github-advisory

## Affected
- Maven: `com.yetanalytics:lrs` — affected >=0 <1.2.17

## Details
### Impact
A maliciously crafted xAPI statement could be used to perform script or other tag injection in the LRS Statement Browser.

### Patches
The problem is patched in version 1.2.17 of the LRS library and [version 0.7.5 of SQL LRS](https://github.com/yetanalytics/lrsql/releases/tag/v0.7.5).

### Workarounds
No workarounds exist, we recommend upgrading to version 1.2.17 of the library or version 0.7.5 of SQL LRS immediately.

### References
* [LRS Tag](https://github.com/yetanalytics/lrs/releases/tag/v1.2.17)
* [LRS lib on Clojars](https://clojars.org/com.yetanalytics/lrs/versions/1.2.17)
* [SQL LRS 0.7.5 Release](https://github.com/yetanalytics/lrsql/releases/tag/v0.7.5)

## References
- https://github.com/yetanalytics/lrs/security/advisories/GHSA-7rw2-3hhp-rc46
- https://nvd.nist.gov/vuln/detail/CVE-2024-26140
- https://github.com/yetanalytics/lrs/commit/d7f4883bc2252337d25e8bba2c7f9d172f5b0621
- https://clojars.org/com.yetanalytics/lrs/versions/1.2.17
- https://github.com/yetanalytics/lrs
- https://github.com/yetanalytics/lrs/releases/tag/v1.2.17
- https://github.com/yetanalytics/lrsql/releases/tag/v0.7.5
