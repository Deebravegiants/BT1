# [C] bsock uses weak hashing algorithms

## Summary
Severity: Critical
Advisory: GHSA-jj93-39pf-7mcf
CVE: CVE-2023-50475
CWE: CWE-327
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-jj93-39pf-7mcf
Type: github-advisory

## Affected
- npm: `bsock` — affected >=0

## Details
An issue was discovered in the bsock component of bcoin-org bcoin that allows remote attackers to obtain sensitive information via weak hashing algorithms in the component `\vendor\faye-websocket.js`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50475
- https://github.com/bcoin-org/bcoin/issues/1174
- https://github.com/bcoin-org/bcoin
- https://github.com/bcoin-org/bcoin/blob/master/node_modules/bsock/package.json
- https://github.com/bcoin-org/bsock/blob/master/package.json
- https://github.com/tianjk99/Cryptographic-Misuses/blob/main/CVE-2023-50475.md
