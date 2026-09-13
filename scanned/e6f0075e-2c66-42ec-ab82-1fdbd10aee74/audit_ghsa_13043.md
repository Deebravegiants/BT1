# [M] MongoDB Driver may publish events containing authentication-related data

## Summary
Severity: Medium
Advisory: GHSA-vxvm-qww3-2fh7
CVE: CVE-2021-32050
CWE: CWE-200, CWE-532
Ecosystem: Packagist, SwiftURL, npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-vxvm-qww3-2fh7
Type: github-advisory

## Affected
- Packagist: `mongodb/mongodb` — affected >=1.0.0 <1.9.2
- npm: `mongodb` — affected >=3.6.0 <3.6.10
- npm: `mongodb` — affected >=4.0.0 <4.17.0
- npm: `mongodb` — affected >=5.0.0 <5.8.0
- SwiftURL: `github.com/mongodb/mongo-swift-driver` — affected >=1.0.0 <1.1.1

## Details
Some MongoDB Drivers may erroneously publish events containing authentication-related data to a command listener configured by an application. The published events may contain security-sensitive data when specific authentication-related commands are executed.

Without due care, an application may inadvertently expose this sensitive information, e.g., by writing it to a log file. This issue only arises if an application enables the command listener feature (this is not enabled by default).

This issue affects the MongoDB C Driver 1.0.0 prior to 1.17.7, MongoDB PHP Driver 1.0.0 prior to 1.9.2, MongoDB Swift Driver 1.0.0 prior to 1.1.1, MongoDB Node.js Driver 3.6 prior to 3.6.10, MongoDB Node.js Driver 4.0 prior to 4.17.0 and MongoDB Node.js Driver 5.0 prior to 5.8.0. This issue also affects users of the MongoDB C++ Driver dependent on the C driver 1.0.0 prior to 1.17.7 (C++ driver prior to 3.7.0).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32050
- https://github.com/mongodb/mongo-php-driver/pull/1235
- https://github.com/mongodb/mongo-swift-driver/pull/643
- https://github.com/mongodb/mongo-php-driver/commit/4495de8313c0d313e4dde906fc7aedf998ee3748
- https://github.com/mongodb/node-mongodb-native/commit/8c8b4c3b8c55f10fb96f63d3bbfa5d408b4ed7d0
- https://jira.mongodb.org/browse/CDRIVER-3797
- https://jira.mongodb.org/browse/CXX-2028
- https://jira.mongodb.org/browse/NODE-3356
- https://jira.mongodb.org/browse/PHPC-1869
- https://jira.mongodb.org/browse/SWIFT-1229
- https://lists.debian.org/debian-lts-announce/2025/05/msg00027.html
- https://security.netapp.com/advisory/ntap-20231006-0001
