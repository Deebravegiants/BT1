# [H] Improper Input Validation in sails-hook-sockets

## Summary
Severity: High
Advisory: GHSA-f7f4-hqp2-7prc
CVE: CVE-2018-21036
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-07-24
Source: https://github.com/advisories/GHSA-f7f4-hqp2-7prc
Type: github-advisory

## Affected
- npm: `sails-hook-sockets` — affected >=0 <1.5.5

## Details
Sails.js before v1.0.0-46 allows attackers to cause a denial of service with a single request because there is no error handler in sails-hook-sockets to handle an empty pathname in a WebSocket request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21036
- https://github.com/balderdashy/sails-hook-sockets/commit/0533a4864b1920fd8fbb5287bc0889193c5faf44
- https://github.com/balderdashy/sails-hook-sockets/commit/ff02114eaec090ee51db48435cc32d451662606e
- https://github.com/balderdashy/sails-hook-sockets
- https://github.com/balderdashy/sails/blob/56f8276f6501a144a03d1f0f28df4ccdb4ad82e2/CHANGELOG.md
- http://www.openwall.com/lists/oss-security/2020/07/19/1
