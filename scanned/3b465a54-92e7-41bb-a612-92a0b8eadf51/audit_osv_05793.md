# [H] BIT-haproxy-2022-0711

## Summary
Severity: High
Advisory: BIT-haproxy-2022-0711
Aliases: CVE-2022-0711
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2022-0711
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.4.0 <2.4.13

## Details
A flaw was found in the way HAProxy processed HTTP responses containing the "Set-Cookie2" header. This flaw could allow an attacker to send crafted HTTP response packets which lead to an infinite loop, eventually resulting in a denial of service condition. The highest threat from this vulnerability is availability.

## References
- https://access.redhat.com/security/cve/cve-2022-0711
- https://github.com/haproxy/haproxy/commit/bfb15ab34ead85f64cd6da0e9fb418c9cd14cee8
- https://www.debian.org/security/2022/dsa-5102
- https://www.mail-archive.com/haproxy%40formilux.org/msg41833.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-0711
