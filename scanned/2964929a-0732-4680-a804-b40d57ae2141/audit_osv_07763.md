# [H] BIT-varnish-2022-45059

## Summary
Severity: High
Advisory: BIT-varnish-2022-45059
Aliases: CVE-2022-45059
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-varnish-2022-45059
Type: osv

## Affected
- Bitnami: `varnish` — affected >=7.2.0 <7.2.1

## Details
An issue was discovered in Varnish Cache 7.x before 7.1.2 and 7.2.x before 7.2.1. A request smuggling attack can be performed on Varnish Cache servers by requesting that certain headers are made hop-by-hop, preventing the Varnish Cache servers from forwarding critical headers to the backend.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G6ZMOZVBLZXHEV5VRW4I4SOWLQEK5OF5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M4KVVCIQVINQQ2D7ORNARSYALMJUMP3I/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XGF6LFTHXCSYMYUX5HLMVXQH3WHCSFLU/
- https://varnish-cache.org/security/VSV00010.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-45059
