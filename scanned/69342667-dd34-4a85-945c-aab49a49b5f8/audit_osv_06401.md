# [C] BIT-lua-2020-15889

## Summary
Severity: Critical
Advisory: BIT-lua-2020-15889
Aliases: CVE-2020-15889
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2020-15889
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.0 <5.4.1

## Details
Lua 5.4.0 has a getobjname heap-based buffer over-read because youngcollection in lgc.c uses markold for an insufficient number of list members.

## References
- http://lua-users.org/lists/lua-l/2020-07/msg00078.html
- http://lua-users.org/lists/lua-l/2020-12/msg00157.html
- https://github.com/lua/lua/commit/127e7a6c8942b362aa3c6627f44d660a4fb75312
- https://nvd.nist.gov/vuln/detail/CVE-2020-15889
