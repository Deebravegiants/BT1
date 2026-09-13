# [H] Resource exhaustion in engine.io

## Summary
Severity: High
Advisory: GHSA-j4f2-536g-r55m
CVE: CVE-2020-36048
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-j4f2-536g-r55m
Type: github-advisory

## Affected
- npm: `engine.io` — affected >=0 <3.6.0

## Details
Engine.IO before 4.0.0 and 3.6.0 allows attackers to cause a denial of service (resource consumption) via a POST request to the long polling transport.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36048
- https://github.com/socketio/engine.io/commit/58e274c437e9cbcf69fd913c813aad8fbd253703
- https://github.com/socketio/engine.io/commit/734f9d1268840722c41219e69eb58318e0b2ac6b
- https://blog.caller.xyz/socketio-engineio-dos
- https://github.com/bcaller/kill-engine-io
- https://github.com/socketio/engine.io
