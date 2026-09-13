# [H] Prototype Pollution in async

## Summary
Severity: High
Advisory: GHSA-fwr7-v2mv-hh25
CVE: CVE-2021-43138
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-07
Source: https://github.com/advisories/GHSA-fwr7-v2mv-hh25
Type: github-advisory

## Affected
- npm: `async` — affected >=3.0.0 <3.2.2
- npm: `async` — affected >=2.0.0 <2.6.4

## Details
A vulnerability exists in Async through 3.2.1 for 3.x and through 2.6.3 for 2.x (fixed in 3.2.2 and 2.6.4), which could let a malicious user obtain privileges via the `mapValues()` method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43138
- https://github.com/caolan/async/pull/1828
- https://github.com/caolan/async/commit/8f7f90342a6571ba1c197d747ebed30c368096d2
- https://github.com/caolan/async/commit/e1ecdbf79264f9ab488c7799f4c76996d5dca66d
- https://github.com/caolan/async
- https://github.com/caolan/async/blob/master/lib/internal/iterator.js
- https://github.com/caolan/async/blob/master/lib/mapValuesLimit.js
- https://github.com/caolan/async/blob/v2.6.4/CHANGELOG.md#v264
- https://github.com/caolan/async/compare/v2.6.3...v2.6.4
- https://jsfiddle.net/oz5twjd9
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MTEUUTNIEBHGKUKKLNUZSV7IEP6IP3Q3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UM6XJ73Q3NAM5KSGCOKJ2ZIA6GUWUJLK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MTEUUTNIEBHGKUKKLNUZSV7IEP6IP3Q3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UM6XJ73Q3NAM5KSGCOKJ2ZIA6GUWUJLK
- https://security.netapp.com/advisory/ntap-20240621-0006
