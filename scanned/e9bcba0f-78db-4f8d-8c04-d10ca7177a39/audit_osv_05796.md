# [C] BIT-haproxy-2023-25725

## Summary
Severity: Critical
Advisory: BIT-haproxy-2023-25725
Aliases: CVE-2023-25725
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2023-25725
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.7.0 <2.7.3

## Details
HAProxy before 2.7.3 may allow a bypass of access control because HTTP/1 headers are inadvertently lost in some situations, aka "request smuggling." The HTTP header parsers in HAProxy may accept empty header field names, which could be used to truncate the list of HTTP headers and thus make some headers disappear after being parsed and processed for HTTP/1.0 and HTTP/1.1. For HTTP/2 and HTTP/3, the impact is limited because the headers disappear before being parsed and processed, as if they had not been sent by the client. The fixed versions are 2.7.3, 2.6.9, 2.5.12, 2.4.22, 2.2.29, and 2.0.31.

## References
- https://git.haproxy.org/?p=haproxy-2.7.git%3Ba=commit%3Bh=a0e561ad7f29ed50c473f5a9da664267b60d1112
- https://lists.debian.org/debian-lts-announce/2023/02/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FPTJQHKUEU2PQ7RWFUYAFLAD4STEIKHU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JM5NCIBTHYDTLPY2UNC4HO2VAHHE6CJG/
- https://www.debian.org/security/2023/dsa-5348
- https://www.haproxy.org/
- https://nvd.nist.gov/vuln/detail/CVE-2023-25725
