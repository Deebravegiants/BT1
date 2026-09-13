# [M] BIT-haproxy-2024-49214

## Summary
Severity: Medium
Advisory: BIT-haproxy-2024-49214
Aliases: CVE-2024-49214
Ecosystem: Bitnami
Published: 2024-10-22
Source: https://osv.dev/vulnerability/BIT-haproxy-2024-49214
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=3.0.0 <3.0.5

## Details
QUIC in HAProxy 3.1.x before 3.1-dev7, 3.0.x before 3.0.5, and 2.9.x before 2.9.11 allows opening a 0-RTT session with a spoofed IP address. This can bypass the IP allow/block list functionality.

## References
- https://github.com/haproxy/haproxy/commit/f627b9272bd8ffca6f2f898bfafc6bf0b84b7d46
- https://www.haproxy.org/download/2.9/src/CHANGELOG
- https://www.haproxy.org/download/3.0/src/CHANGELOG
- https://www.haproxy.org/download/3.1/src/CHANGELOG
- https://www.mail-archive.com/haproxy%40formilux.org/msg45291.html
- https://www.mail-archive.com/haproxy%40formilux.org/msg45314.html
- https://www.mail-archive.com/haproxy%40formilux.org/msg45315.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-49214
