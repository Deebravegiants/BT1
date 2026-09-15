# [M] Insecure Defaults Allow MITM Over TLS in engine.io-client

## Summary
Severity: Medium
Advisory: GHSA-4r4m-hjwj-43p8
CVE: CVE-2016-10536
CWE: CWE-300
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-4r4m-hjwj-43p8
Type: github-advisory

## Affected
- npm: `engine.io-client` — affected >=0 <1.6.9

## Details
Affected versions of `engine.io-client` do not verify certificates by default, and as such may be vulnerable to Man-in-the-Middle attacks.

The vulnerability is related to the way that node.js handles the `rejectUnauthorized` setting. If the value is something that evaluates to false, such as undefined or null, certificate verification will be disabled. 



## Recommendation

Update to version 1.6.9 or later.

If you are unable to upgrade, ensure all calls to socket.io to have a `rejectedUnauthorized: true` flag.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10536
- https://github.com/socketio/engine.io-client/commit/2c55b278a491bf45313ecc0825cf800e2f7ff5c1
- https://github.com/advisories/GHSA-4r4m-hjwj-43p8
- https://www.cigital.com/blog/node-js-socket-io
- https://www.npmjs.com/advisories/99
