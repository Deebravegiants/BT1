# [M] BIT-varnish-2021-36740

## Summary
Severity: Medium
Advisory: BIT-varnish-2021-36740
Aliases: CVE-2021-36740
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-varnish-2021-36740
Type: osv

## Affected
- Bitnami: `varnish` — affected >=6.1.0 <6.6.1

## Details
Varnish Cache, with HTTP/2 enabled, allows request smuggling and VCL authorization bypass via a large Content-Length header for a POST request. This affects Varnish Enterprise 6.0.x before 6.0.8r3, and Varnish Cache 5.x and 6.x before 6.5.2, 6.6.x before 6.6.1, and 6.0 LTS before 6.0.8.

## References
- https://docs.varnish-software.com/security/VSV00007/
- https://github.com/varnishcache/varnish-cache/commit/82b0a629f60136e76112c6f2c6372cce77b683be
- https://github.com/varnishcache/varnish-cache/commit/9be22198e258d0e7a5c41f4291792214a29405cf
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/THV2DQA2GS65HUCKK4KSD2XLN3AAQ2V5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZHBNLDEOTGYRIEQZBWV7F6VPYS4O2AAK/
- https://varnish-cache.org/security/VSV00007.html
- https://www.debian.org/security/2022/dsa-5088
- https://nvd.nist.gov/vuln/detail/CVE-2021-36740
