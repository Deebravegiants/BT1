# [H] Undici has Unhandled Exception in WebSocket Client Due to Invalid server_max_window_bits Validation

## Summary
Severity: High
Advisory: GHSA-v9p9-hfj2-hcw8
CVE: CVE-2026-2229
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-v9p9-hfj2-hcw8
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <6.24.0
- npm: `undici` — affected >=7.0.0 <7.24.0

## Details
### Impact

The undici WebSocket client is vulnerable to a denial-of-service attack due to improper validation of the `server_max_window_bits` parameter in the permessage-deflate extension. When a WebSocket client connects to a server, it automatically advertises support for permessage-deflate compression. A malicious server can respond with an out-of-range `server_max_window_bits` value (outside zlib's valid range of 8-15). When the server subsequently sends a compressed frame, the client attempts to create a zlib InflateRaw instance with the invalid windowBits value, causing a synchronous RangeError exception that is not caught, resulting in immediate process termination.

The vulnerability exists because:

1. The `isValidClientWindowBits()` function only validates that the value contains ASCII digits, not that it falls within the valid range 8-15
2. The `createInflateRaw()` call is not wrapped in a try-catch block
3. The resulting exception propagates up through the call stack and crashes the Node.js process

### Patches
_Has the problem been patched? What versions should users upgrade to?_

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-v9p9-hfj2-hcw8
- https://nvd.nist.gov/vuln/detail/CVE-2026-2229
- https://hackerone.com/reports/3487486
- https://cna.openjsf.org/security-advisories.html
- https://datatracker.ietf.org/doc/html/rfc7692
- https://github.com/nodejs/undici
- https://nodejs.org/api/zlib.html#class-zlibinflateraw
