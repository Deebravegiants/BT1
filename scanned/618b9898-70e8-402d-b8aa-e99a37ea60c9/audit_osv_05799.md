# [H] BIT-haproxy-2023-45539

## Summary
Severity: High
Advisory: BIT-haproxy-2023-45539
Aliases: CVE-2023-45539
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2023-45539
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=0 <2.8.2

## Details
HAProxy before 2.8.2 accepts # as part of the URI component, which might allow remote attackers to obtain sensitive information or have unspecified other impact upon misinterpretation of a path_end rule, such as routing index.html#.png to a static server.

## References
- https://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=2eab6d354322932cfec2ed54de261e4347eca9a6
- https://lists.debian.org/debian-lts-announce/2023/12/msg00010.html
- https://lists.w3.org/Archives/Public/ietf-http-wg/2023JulSep/0070.html
- https://www.mail-archive.com/haproxy%40formilux.org/msg43861.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-45539
