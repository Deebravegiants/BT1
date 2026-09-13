# [H] BIT-openresty-2024-33452

## Summary
Severity: High
Advisory: BIT-openresty-2024-33452
Aliases: CVE-2024-33452
Ecosystem: Bitnami
Published: 2025-06-24
Source: https://osv.dev/vulnerability/BIT-openresty-2024-33452
Type: osv

## Affected
- Bitnami: `openresty` — affected >=0 <1.25.3

## Details
An issue in OpenResty lua-nginx-module v.0.10.26 and before allows a remote attacker to conduct HTTP request smuggling via a crafted HEAD request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33452
- https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
- https://www.benasin.space/2025/03/18/OpenResty-lua-nginx-module-v0-10-26-HTTP-Request-Smuggling-in-HEAD-requests/
- https://lists.debian.org/debian-lts-announce/2025/06/msg00026.html
