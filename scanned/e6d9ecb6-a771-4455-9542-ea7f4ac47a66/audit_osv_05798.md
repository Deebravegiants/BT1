# [H] BIT-haproxy-2023-40225

## Summary
Severity: High
Advisory: BIT-haproxy-2023-40225
Aliases: CVE-2023-40225
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2023-40225
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.8.0 <2.8.2

## Details
HAProxy through 2.0.32, 2.1.x and 2.2.x through 2.2.30, 2.3.x and 2.4.x through 2.4.23, 2.5.x and 2.6.x before 2.6.15, 2.7.x before 2.7.10, and 2.8.x before 2.8.2 forwards empty Content-Length headers, violating RFC 9110 section 8.6. In uncommon cases, an HTTP/1 server behind HAProxy may interpret the payload as an extra request.

## References
- https://cwe.mitre.org/data/definitions/436.html
- https://github.com/haproxy/haproxy/commit/6492f1f29d738457ea9f382aca54537f35f9d856
- https://github.com/haproxy/haproxy/issues/2237
- https://www.haproxy.org/download/2.6/src/CHANGELOG
- https://www.haproxy.org/download/2.7/src/CHANGELOG
- https://www.haproxy.org/download/2.8/src/CHANGELOG
- https://nvd.nist.gov/vuln/detail/CVE-2023-40225
