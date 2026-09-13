# [H] BIT-node-2025-59464

## Summary
Severity: High
Advisory: BIT-node-2025-59464
Aliases: BIT-node-min-2025-59464, CVE-2025-59464
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-node-2025-59464
Type: osv

## Affected
- Bitnami: `node` — affected >=24.0.0 <24.12.0

## Details
A memory leak in Node.js’s OpenSSL integration occurs when converting `X.509` certificate fields to UTF-8 without freeing the allocated buffer. When applications call `socket.getPeerCertificate(true)`, each certificate field leaks memory, allowing remote clients to trigger steady memory growth through repeated TLS connections. Over time this can lead to resource exhaustion and denial of service.

## References
- https://nodejs.org/en/blog/vulnerability/december-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-59464
