# [M] BIT-openresty-2020-36309

## Summary
Severity: Medium
Advisory: BIT-openresty-2020-36309
Aliases: CVE-2020-36309
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openresty-2020-36309
Type: osv

## Affected
- Bitnami: `openresty` — affected >=0 <0.10.16

## Details
ngx_http_lua_module (aka lua-nginx-module) before 0.10.16 in OpenResty allows unsafe characters in an argument when using the API to mutate a URI, or a request or response header.

## References
- https://github.com/openresty/lua-nginx-module/compare/v0.10.15...v0.10.16
- https://github.com/openresty/lua-nginx-module/pull/1654
- https://news.ycombinator.com/item?id=26712562
- https://security.netapp.com/advisory/ntap-20210507-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2020-36309
- https://lists.debian.org/debian-lts-announce/2025/06/msg00026.html
