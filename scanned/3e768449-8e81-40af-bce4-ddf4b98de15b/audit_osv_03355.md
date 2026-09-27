# [H] ALPINE-CVE-2025-59465

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-59465
Ecosystem: Alpine:v3.21, Alpine:v3.22
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-59465
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.0-r0

## Details
A malformed `HTTP/2 HEADERS` frame with oversized, invalid `HPACK` data can cause Node.js to crash by triggering an unhandled `TLSSocket` error `ECONNRESET`. Instead of safely closing the connection, the process crashes, enabling a remote denial of service. This primarily affects applications that do not attach explicit error handlers to secure sockets, for example:
```
server.on('secureConnection', socket => {
  socket.on('error', err => {
    console.log(err)
  })
})
```

## References
- https://security.alpinelinux.org/vuln/CVE-2025-59465
