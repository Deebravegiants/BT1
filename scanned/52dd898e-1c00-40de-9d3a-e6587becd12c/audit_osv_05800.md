# [H] BIT-haproxy-2024-45506

## Summary
Severity: High
Advisory: BIT-haproxy-2024-45506
Aliases: CVE-2024-45506
Ecosystem: Bitnami
Published: 2025-09-11
Source: https://osv.dev/vulnerability/BIT-haproxy-2024-45506
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=3.0.0 <3.0.4

## Details
HAProxy 2.9.x before 2.9.10, 3.0.x before 3.0.4, and 3.1.x through 3.1-dev6 allows a remote denial of service for HTTP/2 zero-copy forwarding (h2_send loop) under a certain set of conditions, as exploited in the wild in 2024.

## References
- http://git.haproxy.org/?p=haproxy-3.0.git%3Ba=commitdiff%3Bh=c725db17e8416ffb3c1537aea756356228ce5e3c
- http://git.haproxy.org/?p=haproxy-3.0.git%3Ba=commitdiff%3Bh=d636e515453320c6e122c313c661a8ac7d387c7f
- https://nvd.nist.gov/vuln/detail/CVE-2024-45506
- https://www.haproxy.org/
- https://www.haproxy.org/download/3.1/src/CHANGELOG
- https://www.mail-archive.com/haproxy%40formilux.org/msg45280.html
- https://www.mail-archive.com/haproxy%40formilux.org/msg45281.html
