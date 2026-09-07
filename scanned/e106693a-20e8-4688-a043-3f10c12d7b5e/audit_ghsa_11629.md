# [H] Undici has Unbounded Memory Consumption in WebSocket permessage-deflate Decompression

## Summary
Severity: High
Advisory: GHSA-vrm6-8vpv-qv8q
CVE: CVE-2026-1526
CWE: CWE-409
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-vrm6-8vpv-qv8q
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <6.24.0
- npm: `undici` — affected >=7.0.0 <7.24.0

## Details
## Description

The undici WebSocket client is vulnerable to a denial-of-service attack via unbounded memory consumption during permessage-deflate decompression. When a WebSocket connection negotiates the permessage-deflate extension, the client decompresses incoming compressed frames without enforcing any limit on the decompressed data size. A malicious WebSocket server can send a small compressed frame (a "decompression bomb") that expands to an extremely large size in memory, causing the Node.js process to exhaust available memory and crash or become unresponsive.

The vulnerability exists in the `PerMessageDeflate.decompress()` method, which accumulates all decompressed chunks in memory and concatenates them into a single Buffer without checking whether the total size exceeds a safe threshold.

## Impact

- Remote denial of service against any Node.js application using undici's WebSocket client
- A single compressed WebSocket frame of ~6 MB can decompress to ~1 GB or more
- Memory exhaustion occurs in native/external memory, bypassing V8 heap limits
- No application-level mitigation is possible as decompression occurs before message delivery

### Patches

Users should upgrade to fixed versions.

### Workarounds

No workaround are possible.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-vrm6-8vpv-qv8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-1526
- https://hackerone.com/reports/3481206
- https://cna.openjsf.org/security-advisories.html
- https://datatracker.ietf.org/doc/html/rfc7692
- https://github.com/nodejs/undici
- https://owasp.org/www-community/attacks/Denial_of_Service
