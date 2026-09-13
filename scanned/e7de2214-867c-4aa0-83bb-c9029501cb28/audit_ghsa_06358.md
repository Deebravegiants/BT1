# [H] Socket.IO: Zero-attachment Memory Exhaustion

## Summary
Severity: High
Advisory: GHSA-2m8v-j782-fhvr
CVE: CVE-2026-69185
CWE: CWE-20, CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-2m8v-j782-fhvr
Type: github-advisory

## Affected
- npm: `socket.io-parser` — affected >=4.0.0 <4.2.7
- npm: `socket.io-parser` — affected >=3.4.0 <3.4.5
- npm: `socket.io-parser` — affected >=0 <3.3.6

## Details
### Impact

A specially crafted Socket.IO packet can make the server wait for a large number of binary attachments and buffer them, which can be exploited to make the server run out of memory.

### Patches

| Version range    | Used by                                    | Fixed version |
|------------------|--------------------------------------------|---------------|
| `>=4.0.0 <4.2.7` | `socket.io@4.x` and `socket.io-client@4.x` | `4.2.7`       |
| `>=3.4.0 <3.4.5` | `socket.io@2.x`                            | `3.4.5`       |
| `<3.3.6`         | `socket.io-client@2.x`                     | `3.3.6`       |

### Workarounds

There is no known workaround except upgrading to a safe version.

### For more information

If you have any questions or comments about this advisory:

- Open a discussion [here](https://github.com/socketio/socket.io/discussions)

## References
- https://github.com/socketio/socket.io/security/advisories/GHSA-2m8v-j782-fhvr
- https://github.com/socketio/socket.io/commit/7c6ef571a00656718e9e05e3b948fd1758b2a7b4
- https://github.com/socketio/socket.io/commit/9c6323e5cde41bd75df3379b5fc9293664a5f240
- https://github.com/socketio/socket.io/commit/ced94ffa3ac020a8f3c14eb98a3bf34acb14d291
- https://github.com/socketio/socket.io
