# [M] decode-uri-component: Denial of service via exponential decoding of malformed percent-encoded input

## Summary
Severity: Medium
Advisory: GHSA-vcc3-ghjq-m6fr
CVE: CVE-2026-45822
CWE: CWE-1176, CWE-400, CWE-405, CWE-407
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/S:N/AU:Y/R:U/V:D/RE:M/U:Amber (CVSS_V4)
Published: 2026-08-31
Source: https://github.com/advisories/GHSA-vcc3-ghjq-m6fr
Type: github-advisory

## Affected
- npm: `decode-uri-component` — affected >=0 <0.5.0

## Details
### Impact
An attacker who can supply input to `decodeUriComponent()` (directly or via a dependency that uses this package on URL/query/path data) can cause excessive CPU usage and application unresponsiveness. This is an availability issue; there is no known memory corruption, data disclosure, or remote code execution impact.

### Patches
Upgrade to `decode-uri-component@0.5.0`.

### Workarounds
Limit the size of the input.

## References
- https://github.com/SamVerschueren/decode-uri-component/security/advisories/GHSA-vcc3-ghjq-m6fr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45822
- https://github.com/SamVerschueren/decode-uri-component/commit/fa479dafeede7bedf04e5c89aa78f2a78c664005
- https://github.com/SamVerschueren/decode-uri-component
- https://github.com/SamVerschueren/decode-uri-component/blob/00662938dc7c6241547ae8abce7785cc13ffd3f6/index.js
- https://github.com/SamVerschueren/decode-uri-component/releases/tag/v0.5.0
- https://www.npmjs.com/package/decode-uri-component
