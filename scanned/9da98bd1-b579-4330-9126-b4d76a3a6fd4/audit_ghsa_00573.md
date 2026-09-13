# [H] Insecure randomness in socket.io

## Summary
Severity: High
Advisory: GHSA-qv2v-m59f-v5fw
CVE: CVE-2017-16031
CWE: CWE-330
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-11-07
Source: https://github.com/advisories/GHSA-qv2v-m59f-v5fw
Type: github-advisory

## Affected
- npm: `socket.io` — affected >=0 <0.9.7

## Details
Affected versions of `socket.io` depend on `Math.random()` to create socket IDs, and therefore the IDs are predictable. With enough information on prior IDs, an attacker may be able to guess the socket ID and gain access to socket.io servers without authorization.


## Recommendation

Update to v0.9.7 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16031
- https://github.com/socketio/socket.io/issues/856
- https://github.com/socketio/socket.io/pull/857
- https://github.com/socketio/socket.io/commit/67b4eb9abdf111dfa9be4176d1709374a2b4ded8
- https://github.com/advisories/GHSA-qv2v-m59f-v5fw
- https://github.com/socketio/socket.io
- https://www.npmjs.com/advisories/321
