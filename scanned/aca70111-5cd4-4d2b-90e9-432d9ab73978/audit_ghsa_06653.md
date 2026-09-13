# [H] Apache Camel-Couchbase: Non-Camel-prefixed Exchange headers bypass HeaderFilterStrategy allowing operation override from untrusted input

## Summary
Severity: High
Advisory: GHSA-46jf-c9vx-hh79
CVE: CVE-2026-46587
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-46jf-c9vx-hh79
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-couchbase` — affected >=4.0.0 <4.14.8
- Maven: `org.apache.camel:camel-couchbase` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-couchbase` — affected >=4.19.0 <4.21.0

## Details
Improper Input Validation vulnerability in Apache Camel.

This issue affects Apache Camel: through 4.14.7, from 4.15.0 through 4.18.2, from 4.19.0 through 4.20.0.

Users are recommended to upgrade to version 4.14.8, 4.18.3, 4.21.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46587
- https://github.com/apache/camel/pull/23228
- https://github.com/apache/camel/pull/23230
- https://github.com/apache/camel/pull/23231
- https://github.com/apache/camel/commit/8d74cdca9befc74b49d9c52ac6a145be1d413e7d
- https://github.com/apache/camel/commit/c16f7ef39849ae8819f50c959b538350b8f839e9
- https://github.com/apache/camel/commit/d0dfa4e0ebd062acaf4a86ca476bb4305db9bfd4
- https://camel.apache.org/security/CVE-2026-46587.html
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.14.8
- https://github.com/apache/camel/releases/tag/camel-4.18.3
- https://github.com/apache/camel/releases/tag/camel-4.21.0
- http://www.openwall.com/lists/oss-security/2026/07/06/15
