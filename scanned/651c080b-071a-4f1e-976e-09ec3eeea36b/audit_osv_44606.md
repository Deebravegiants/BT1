# [M] undici vulnerable to Denial of Service via WebSocketStream unclean close

## Summary
Severity: Medium
Advisory: CVE-2026-85014
Aliases: GHSA-rx4f-c7p8-82vq
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85014
Type: osv

## Details
undici's experimental WebSocketStream client crashes the whole Node.js process when a remote peer closes the TCP connection without a WebSocket close handshake. On an unclean close the internal socket-close handler calls abort on the writable stream unconditionally and discards the returned promise, but per the WHATWG Streams standard aborting a locked writable returns a promise that rejects with a TypeError. Because the application holds a writer on that writable, which is the only way to write, the rejection is never observed and Node's default unhandled-rejection behavior terminates the process. An untrusted server can therefore crash a client with a single abrupt disconnect, with no authentication and no application mistake. This affects undici versions from 7.0.0 up to 7.29.1 and from 8.0.0 up to 8.10.2. Users should upgrade to undici 7.29.1 or 8.10.2.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85014.json
- https://github.com/nodejs/undici/security/advisories/GHSA-rx4f-c7p8-82vq
- https://nvd.nist.gov/vuln/detail/CVE-2026-85014
