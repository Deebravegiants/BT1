# [H] Resource exhaustion in socket.io-parser

## Summary
Severity: High
Advisory: GHSA-xfhh-g9f5-x4m4
CVE: CVE-2020-36049
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-30
Source: https://github.com/advisories/GHSA-xfhh-g9f5-x4m4
Type: github-advisory

## Affected
- npm: `socket.io-parser` — affected >=0 <3.3.2
- npm: `socket.io-parser` — affected >=3.4.0 <3.4.1

## Details
The `socket.io-parser` npm package before versions 3.3.2 and 3.4.1 allows attackers to cause a denial of service (memory consumption) via a large packet because a concatenation approach is used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36049
- https://github.com/socketio/socket.io-parser/commit/dcb942d24db97162ad16a67c2a0cf30875342d55
- https://blog.caller.xyz/socketio-engineio-dos
- https://github.com/bcaller/kill-engine-io
- https://github.com/socketio/socket.io-parser/releases/tag/3.3.2
- https://github.com/socketio/socket.io-parser/releases/tag/3.4.1
- https://www.npmjs.com/package/socket.io-parser
