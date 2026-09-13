# [H] qs vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-hrpp-h998-j3pp
CVE: CVE-2022-24999
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-27
Source: https://github.com/advisories/GHSA-hrpp-h998-j3pp
Type: github-advisory

## Affected
- npm: `qs` — affected >=6.10.0 <6.10.3
- npm: `qs` — affected >=6.9.0 <6.9.7
- npm: `qs` — affected >=6.8.0 <6.8.3
- npm: `qs` — affected >=6.7.0 <6.7.3
- npm: `qs` — affected >=6.6.0 <6.6.1
- npm: `qs` — affected >=6.5.0 <6.5.3
- npm: `qs` — affected >=6.4.0 <6.4.1
- npm: `qs` — affected >=6.3.0 <6.3.3
- npm: `qs` — affected >=0 <6.2.4

## Details
qs before 6.10.3 allows attackers to cause a Node process hang because an `__ proto__` key can be used. In many typical web framework use cases, an unauthenticated remote attacker can place the attack payload in the query string of the URL that is used to visit the application, such as `a[__proto__]=b&a[__proto__]&a[length]=100000000`. The fix was backported to qs 6.9.7, 6.8.3, 6.7.3, 6.6.1, 6.5.3, 6.4.1, 6.3.3, and 6.2.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24999
- https://github.com/ljharb/qs/pull/428
- https://github.com/ljharb/qs/commit/4310742efbd8c03f6495f07906b45213da0a32ec
- https://github.com/ljharb/qs/commit/727ef5d34605108acb3513f72d5435972ed15b68
- https://github.com/ljharb/qs/commit/73205259936317b40f447c5cdb71c5b341848e1b
- https://github.com/ljharb/qs/commit/8b4cc14cda94a5c89341b77e5fe435ec6c41be2d
- https://github.com/ljharb/qs/commit/ba24e74dd17931f825adb52f5633e48293b584e1
- https://github.com/ljharb/qs/commit/e799ba57e573a30c14b67c1889c7c04d508b9105
- https://github.com/ljharb/qs/commit/ed0f5dcbef4b168a8ae299d78b1e4a2e9b1baf1f
- https://github.com/ljharb/qs/commit/f945393cfe442fe8c6e62b4156fd35452c0686ee
- https://github.com/ljharb/qs/commit/fc3682776670524a42e19709ec4a8138d0d7afda
- https://github.com/expressjs/express/releases/tag/4.17.3
- https://github.com/ljharb/qs
- https://github.com/n8tz/CVE-2022-24999
- https://lists.debian.org/debian-lts-announce/2023/01/msg00039.html
- https://security.netapp.com/advisory/ntap-20230908-0005
