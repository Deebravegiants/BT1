# [H] BIT-varnish-2022-45060

## Summary
Severity: High
Advisory: BIT-varnish-2022-45060
Aliases: CVE-2022-45060
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-varnish-2022-45060
Type: osv

## Affected
- Bitnami: `varnish` — affected >=7.2.0 <7.2.1

## Details
An HTTP Request Forgery issue was discovered in Varnish Cache 5.x and 6.x before 6.0.11, 7.x before 7.1.2, and 7.2.x before 7.2.1. An attacker may introduce characters through HTTP/2 pseudo-headers that are invalid in the context of an HTTP/1 request line, causing the Varnish server to produce invalid HTTP/1 requests to the backend. This could, in turn, be used to exploit vulnerabilities in a server behind the Varnish server. Note: the 6.0.x LTS series (before 6.0.11) is affected.

## References
- https://docs.varnish-software.com/security/VSV00011
- https://lists.debian.org/debian-lts-announce/2022/11/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G6ZMOZVBLZXHEV5VRW4I4SOWLQEK5OF5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M4KVVCIQVINQQ2D7ORNARSYALMJUMP3I/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XGF6LFTHXCSYMYUX5HLMVXQH3WHCSFLU/
- https://varnish-cache.org/security/VSV00011.html
- https://www.debian.org/security/2023/dsa-5334
- https://nvd.nist.gov/vuln/detail/CVE-2022-45060
