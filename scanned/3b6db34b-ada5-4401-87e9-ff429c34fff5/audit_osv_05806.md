# [M] BIT-haproxy-2026-33555

## Summary
Severity: Medium
Advisory: BIT-haproxy-2026-33555
Aliases: CVE-2026-33555
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-haproxy-2026-33555
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.6.0 <3.3.6

## Details
An issue was discovered in HAProxy before 3.3.6. The HTTP/3 parser does not check that the received body length matches a previously announced content-length when the stream is closed via a frame with an empty payload. This can cause desynchronization issues with the backend server and could be used for request smuggling. The earliest affected version is 2.6.

## References
- https://github.com/haproxy/haproxy/commit/05a295441c621089ffa4318daf0dbca2dd756a84
- https://nvd.nist.gov/vuln/detail/CVE-2026-33555
- https://r3verii.github.io/cve/2026/04/14/haproxy-h3-standalone-fin-smuggling.html
- https://www.haproxy.com/documentation/haproxy-aloha/changelog/
- https://www.haproxy.org
- https://www.mail-archive.com/haproxy@formilux.org/msg46752.html
