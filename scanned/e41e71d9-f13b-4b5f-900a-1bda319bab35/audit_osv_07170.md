# [H] BIT-node-2025-59465

## Summary
Severity: High
Advisory: BIT-node-2025-59465
Aliases: BIT-node-min-2025-59465, CVE-2025-59465
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-node-2025-59465
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.3.0

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
- https://nodejs.org/en/blog/vulnerability/december-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-59465
- https://access.redhat.com/errata/RHSA-2026:1842
- https://access.redhat.com/errata/RHSA-2026:1843
- https://access.redhat.com/errata/RHSA-2026:2420
- https://access.redhat.com/errata/RHSA-2026:2421
- https://access.redhat.com/errata/RHSA-2026:2422
- https://access.redhat.com/errata/RHSA-2026:2767
- https://access.redhat.com/errata/RHSA-2026:2768
- https://access.redhat.com/errata/RHSA-2026:2781
- https://access.redhat.com/errata/RHSA-2026:2782
- https://access.redhat.com/errata/RHSA-2026:2783
- https://access.redhat.com/errata/RHSA-2026:2864
- https://access.redhat.com/errata/RHSA-2026:2899
- https://access.redhat.com/errata/RHSA-2026:6402
- https://access.redhat.com/errata/RHSA-2026:6431
- https://access.redhat.com/errata/RHSA-2026:7386
- https://access.redhat.com/errata/RHSA-2026:7387
- https://access.redhat.com/security/cve/CVE-2025-59465
- https://bugzilla.redhat.com/show_bug.cgi?id=2431349
