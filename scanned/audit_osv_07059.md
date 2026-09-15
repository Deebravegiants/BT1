# [H] BIT-nginx-2021-3618

## Summary
Severity: High
Advisory: BIT-nginx-2021-3618
Aliases: BIT-nginx-gateway-2021-3618, CVE-2021-3618
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-nginx-2021-3618
Type: osv

## Affected
- Bitnami: `nginx` — affected >=0 <1.21.0

## Details
ALPACA is an application layer protocol content confusion attack, exploiting TLS servers implementing different protocols but using compatible certificates, such as multi-domain or wildcard certificates. A MiTM attacker having access to victim's traffic at the TCP/IP layer can redirect traffic from one subdomain to another, resulting in a valid TLS session. This breaks the authentication of TLS and cross-protocol attacks may be possible where the behavior of one protocol service may compromise the other at the application layer.

## References
- https://alpaca-attack.com/
- https://bugzilla.redhat.com/show_bug.cgi?id=1975623
- https://lists.debian.org/debian-lts-announce/2022/11/msg00031.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-3618
