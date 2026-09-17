# [H] undici vulnerable to Denial of Service via unrequested WebSocket subprotocol

## Summary
Severity: High
Advisory: CVE-2026-19534
Aliases: GHSA-rfgv-xxqx-mfg5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-19534
Type: osv

## Details
undici's WebSocket client crashes the whole Node.js process during the opening handshake when a server responds with a subprotocol that the client never requested. A default WebSocket connection sends no subprotocol, but if the server's 101 response includes a Sec-WebSocket-Protocol header, undici dereferences a null value while checking it against the requested list and throws an uncaught TypeError. Because that code runs inside a microtask with no surrounding error handling, the exception propagates and terminates the process under Node's default behavior, instead of gracefully failing the connection as required by the WebSocket protocol. Any application that opens a WebSocket to an attacker-controlled or compromised server, or over a plaintext connection subject to a machine-in-the-middle, can be crashed remotely without authentication in the default configuration. This affects undici versions from 6.7.0 up to 6.28.1, from 7.0.0 up to 7.29.1, and from 8.0.0 up to 8.10.2. Users should upgrade to undici 6.28.1, 7.29.1, or 8.10.2.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19534.json
- https://github.com/nodejs/undici/security/advisories/GHSA-rfgv-xxqx-mfg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-19534
